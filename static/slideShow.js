﻿/*
1. body onload call
    - read cookie and get last image id
    - start to download next image.
        img.src = xxxx
        onload = ...   .push image to queue
    - if queue is filled with 3 or 5 images. go to 2.
2. start transition
    - from current to next.
    - if current is null, fade in with next
3. if find-in is complete, load next image.
4. pop front if size is larger then threthold.

*/
IMAGE_ID = "image_id";
DESC_ID = "imageDesc";
INFO_ID = "info";
SLIDE_DELAY = "slideDelay";
FADE_DELAY = "fadeDelay";
VIDEO_VOLUME = "video_volume";
SET_DATE = "setDate";
START_DATE = "starDate";
END_DATE = "endDate";
DEBUG = "debug";
LAST_UPDATE_TIME = "last_update_time";
LAST_UPDATE_ID = "last_update_id";
UPDATE_COUNT = "update_count";
HISTORY = "obj_history";

QUERY = "query";
ALLOW_TIME = 2 * 60;

MEDIA = "media";
IMAGE1 = "slideimage0";
IMAGE2 = "slideimage1";

DEFAULT_START_DATE = '2000-01-01';
DEFAULT_END_DATE = '2050-12-31';

String.prototype.format = function () {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

/* GLOBALS **********************************************************************************************/

var images = {
    slideDelay: 10000, // The time interval between consecutive slides.
    fadeDelay: 50, // The time interval between individual opacity changes. This should always be much smaller than slideDelay.  
    wrapperID: "slideShowImages", // The ID of the <div> element that contains all of the <img> elements to be shown as a slide show.
    wrapperObject: null, // Will contain a reference to the <div> element that contains all of the <img> elements to be shown as a slide show.

    slideShowID: -1, // A setInterval() ID value used to stop the slide show.
    slideShowRunning: true, // Used to record when the slide show is running and when it's not. The slide show is always initially running.    

    imageObjects: [],
    imageDescObjects: [],
    infoObjects: [],
    width: 0,
    height: 0,
    queue: [],
    curIndex: 1,
    maxQueueSize: 3,
    url: "nextimage",
    dateQuery: null,
    startDate: null,
    endDate:null,
    media: "both",
    videoVolume: "0.5",
    start: false,
    debug: false,
    cur_id: null,
    monitor: null,
    total: 0
}

function createCookie(name, value, days) {
    var expires;

    if (!days) {
        days = 365;
    }

    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toGMTString();

    document.cookie = name + "=" + value + expires + "; path=/";
}

function readCookie(name, def) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');

    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0)
            return c.substring(nameEQ.length, c.length);
    }
    return typeof def !== 'undefined' ? def : null;
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}


//window.addEventListener('load', slideShow, false);

String.prototype.format = function () {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

function sleep(ms) {
    var unixtime_ms = new Date().getTime();
    while (new Date().getTime() < unixtime_ms + ms) { }
}

function set_last_update(id) {
    last_id = readCookie(LAST_UPDATE_ID, "");
//    console.log("***********************************");
//    console.log("last_id=%s, id=%s", last_id, id);

    t = Math.floor(Date.now() / 1000);
    createCookie(LAST_UPDATE_TIME, t);
    createCookie(LAST_UPDATE_ID, id);

//    console.log("update checkpoint. id=%s t=%s", id, t);
}

function check_liveness() {
    last_time = parseInt(readCookie(LAST_UPDATE_TIME));
    last_id = readCookie(LAST_UPDATE_ID, "");

    cur = Math.floor(Date.now() / 1000);
    d = cur - last_time;

    if (d > ALLOW_TIME) {
//        console.log("Page seems DEAD!!!!!!!!!!!!!!!!!!!!!!!!!. diff=%s ALLOW_TIME=%s. Skip id=%d RELOAD",
//            d, ALLOW_TIME, last_id);

        createCookie(UPDATE_COUNT, 0);
        eraseCookie(QUERY);
        location.reload();
    }
    else {
 //       console.log("Page is alive!!!!!!!!!!!!.  diff=%d ALLOW_TIME=%s id=%s ",
 //           d, ALLOW_TIME, last_id);
    }
}

function check_history(id) {
    obj_history = readCookie(HISTORY, "");
//    console.log("#######################   Current history = %s", obj_history);

    list = obj_history.split(',');

    var i = list.length - 1;
    var count = 0;

    while (i >= 0 && list[i] == id) {
        count++;
        i--;
    }

    if (count >= 3) {
 //       console.log("#######################   Too many errors %s ", id);
        return false;
    }

    list.push(id);
    if (list.length > 10)
        list.shift();

    var r = list.join();
 //   console.log("updated history = %s", r);
    createCookie(HISTORY, r);

    return true;
}

function slideShow() {



    /* MAIN *************************************************************************************************/
    console.log("start");
    if (!document.getElementById(images.wrapperID))
        return;

    images.wrapperObject = document.getElementById(images.wrapperID);
    if (!images.wrapperObject)
        return;

    document.body.style.overflow = 'hidden';

    var size = getWindowSize();
    images.width = size.w; // Returns a value that is always in pixel units.
    images.height = size.h; // Returns a value that is always in pixel units.

    images.wrapperObject.style.position = "absolute";
    images.wrapperObject.style.overflow = "hidden"; // This is just a safety thing.
    images.wrapperObject.style.width = images.width + "px";
    images.wrapperObject.style.height = images.height + "px";
    images.wrapperObject.style.top = 0;
    images.wrapperObject.style.left = 0;

    images.imageObjects.push(document.getElementById(IMAGE1));
    images.imageObjects.push(document.getElementById(IMAGE2));

    for (var i = 0; i < images.imageObjects.length; i++) {
        var div = images.imageObjects[i];
        div.style.position = "absolute";
        div.style.overflow = "hidden";
        div.style.opacity = 0;
        div.style.width = images.width + "px";
        div.style.height = images.height + "px";
        div.style.top = 0 + "px";
        div.style.left = 0 + "px";
        div.media_type = "img";

        var desc = div.querySelectorAll('span')[0];
        images.imageDescObjects.push(desc);

        desc.style.position = "absolute";
        desc.style.top = (size.h - 80) + "px";
        desc.style.left = 10 + "px";

        var info = div.querySelectorAll('div')[0];
        images.infoObjects.push(info);

        info.style.position = "absolute";
        //       info.style.top = (size.h - 105) + "px";
        info.style.top = 10 + "px";
        info.style.left = (size.w - 220) + "px";

    }

    //   console.log(images.descObject);
//    console.log("READ COOKIE");
    var id = readCookie(IMAGE_ID, -1);
    //    id = 3483;
    //  id = 7824;

    {
        // for debug purpose.  To set cur_id, set id at the same time
        //    images.cur_id = 16567;
        //    id = images.cur_id;
    }


    images.slideDelay = readCookie(SLIDE_DELAY, images.slideDelay);
    images.fadeDelay = readCookie(FADE_DELAY, images.fadeDelay);
    images.media = readCookie(MEDIA, images.media);
    images.debug = JSON.parse(readCookie(DEBUG, images.debug));
    images.videoVolume = readCookie(VIDEO_VOLUME, images.videoVolume);
    images.startDate = readCookie(START_DATE, DEFAULT_START_DATE);
    images.endDate = readCookie(END_DATE, DEFAULT_END_DATE);
    images.lastQuery = readCookie(QUERY, "");
    images.dateQuery = readCookie(SET_DATE, "");

    if (images.startDate == '')
        images.startDate = DEFAULT_START_DATE;
    if (images.endDate == '')
        images.endDate = DEFAULT_END_DATE;

    console.log("startDate=%s endDate=%s lastQuery=%s ", images.startDate,
        images.endDate, images.lastQuery);


    t = Math.floor(Date.now() / 1000);
    createCookie(LAST_UPDATE_TIME, t);
    createCookie(SET_DATE, "");

    var url = "http://{0}/{1}".format(window.location.host, images.url);

 //   console.log("id=%d, query=%s", id, images.lastQuery);
//    console.log("slideDelay=" + images.slideDelay + " fadeDelay=" + images.fadeDelay + " url=" + url);
    fillImages(url, id, images.queue, images.maxQueueSize);

    images.monitor = setInterval(check_liveness, 10000);

    return;

    /* FUNCTIONS ********************************************************************************************/
    /*
    {
      "address": "Not Found",
      "created": "2015:12:11 15:26:20",
      "id": 6,
      "loc": null,
      "name": "6.jpg",
      "path": "media/6.jpg",
      "type": "img" or "video"
    }
    */
    function print_queue(queue) {
        s = "";
        for (i = 0; i < queue.length; i++)
            s += queue[i].obj["id"] + " ";

  //      console.log(s);
    }


    function video_error(reason, media) {
        console.log("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   [%s] %s", media.obj['id'], reason);

        if (media.loaded == false) {
            console.log("ERROR before Loading!!   [%s] %s", media.obj['id'], reason);
            sleep(5000);
            return;
        }

        set_last_update(media.obj['id']);

        sleep(5000);
        location.reload();
    }

    function check_result(obj) {
        if (obj["created"] < images.startDate || obj["created"] > images.endDate) {

            console.log("No result in date range. id=%s, date=%s, start=%s, end=%s",
                obj["id"], obj["created"], images.startDate, images.endDate);

            images.startDate = DEFAULT_START_DATE;
            images.endDate = DEFAULT_END_DATE;
            createCookie(START_DATE, images.startDate);
            createCookie(END_DATE, images.endDate);

        }
    }

    function fillImages(url, id, queue, maxQueueSize) {
        var query;

//        console.log("call fillImages, id=%s", id);

        if (images.start) {
//            console.log("show already start. Get next of [%s]. queue=%s", id, queue.length)
            //    return;
        }

        if (queue.length >= maxQueueSize) {
            completeImagesLoading();
            return;
        }
//        console.log("call fillImages 2, id=%s", id);

        //console.log("1. url={0} id={1} queue size={2}".format(url, id, queue.length));

        xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                function finish_load(media) {
                    images.queue.push(media);
                    media.loaded = true;
  //                  console.log("[%s] fillImages::finish_load queue size=%s, id=%s", obj['id'], queue.length, id);

                    check_result(media.obj);
                    print_queue(queue);
                    fillImages(url, media.obj['id'], queue, maxQueueSize);
                }

                obj = JSON.parse(xmlhttp.responseText);

 //               console.log("[%s] fillImages::onreadystatechange url=%s obj=%s", obj['id'], url, xmlhttp.responseText);

                if (obj["media_type"] == 'image') {
                    media = new Image();
                    media.type = "img";
  //                  console.log("[%s] fillImages::onreadystatechange load img", obj["id"]);
                    media.onload = function () {
                        finish_load(media);
                    }
                }
                else if (obj["media_type"] == 'video') {
                    media = document.createElement('video');
                    media.type = "video";
 //                   console.log("[%s] fillImages::onreadystatechange  load video", obj["id"]);

                    // https://www.w3schools.com/tags/av_event_canplay.asp
                    media.onloadedmetadata = function () {
                        finish_load(media);
                    }

                    media.onerror = function () {
                        video_error("onerror", media);
                    }
                    media.onstalled = function () {
                        video_error("onstalled", media);
                    }
                    media.onabort = function () {
                        video_error("onabort", media);
                    }
                    media.controls = true;
                }
                else {
                    alert("invalid format=" + obj["media_type"]);
                    return;
                }

                // new Image() vs document.createElement('img')
                // https://stackoverflow.com/questions/6241716/is-there-a-difference-between-new-image-and-document-createelementimg

                media.query = query;
                media.obj = obj;
                media.loaded = false;
                media.src = "http://{0}/{1}".format(window.location.host, obj["path"])
  //              console.log("[%s] fillImages::onreadystatechange  media.src=", obj["id"], media.src);
            }
        }
        xmlhttp.onerror = function () {
            failImageLoading();
        }

        xmlhttp.ontimeout = function () {
            failImageLoading();
        }

        query = "{0}?id={1}&media={2}&start={3}&end={4}".format(url, id, images.media,
            images.startDate, images.endDate);
  //      console.log("images.startDate=%s  endDate=%s", images.startDate, images.endDate);

        if (images.dateQuery == null || images.dateQuery == "") {
            if (queue.length == 0 && (images.cur_id || images.lastQuery)) {
                if (images.cur_id) {
                    query = "{0}?curid={1}&media={2}&start={3}&end={4}".format(url, images.cur_id, images.media,
                            images.startDate, images.endDate);
 //                   console.log("Use cur_id = %s ", query);

                    images.cur_id = null;
                }
                else if (images.lastQuery) {
                    query = images.lastQuery;

   //                 console.log("Use last query = %s", images.lastQuery);
                }
            }
            else {
                query = "{0}?id={1}&media={2}&start={3}&end={4}".format(url, id, images.media,
                    images.startDate, images.endDate);
            }
        }
        else {
            query = "{0}?setdate={1}&media={2}&start={3}&end={4}".format(url, images.dateQuery,
                    images.media, images.startDate, images.endDate);
            images.dateQuery = null;
        }

//        console.log("query=%s", query);

        xmlhttp.open("GET", query, true);
        xmlhttp.timeout = 10000;
        xmlhttp.send();
        //console.log("2. query={0} id={1} queue size={2}".format(query, id, queue.length));
    }

    function fillOneImage(url, queue) {
        var query;

 //       console.log("call fillOneImage");
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                obj = JSON.parse(xmlhttp.responseText);

 //               console.log("{0}", obj);
                if (obj["media_type"] == 'image') {
                    media = new Image();
                    media.type = "img";
 //                   console.log("[%s] fillOneImage::onreadystatechange  load img 1", obj["id"]);
                    media.onload = function () {
                        images.queue.push(media);
                        check_result(media.obj);
                    }
                }
                else if (obj["media_type"] == 'video') {
                    media = document.createElement('video')
                    media.type = "video";

//                    console.log("[%s] fillOneImage::onreadystatechang load video 1", obj["id"]);
                    media.onloadedmetadata = function () {
                        images.queue.push(media);
                        media.loaded = true;
                        check_result(media.obj);

 //                       console.log("[%s] fillOneImage::media.oncanplay queue size=%s", obj['id'], queue.length);
                        print_queue(queue);
                    }
                    media.onerror = function () {
                        video_error("onerror", media);
                    }
                    media.onstalled = function () {
                        video_error("onstalled", media);
                    }
                    media.onabort = function () {
                        video_error("onabort", media);
                    }
                    if (images.debug) {
                        media.controls = true;
                    }
                    else {
                        media.controls = false;
                    }
                }
                else {
                    alert("invalid format=" + obj["type"]);
                    return;
                }

                //console.log("3. url={0} id={1} obj={2}".format(url, id, xmlhttp.responseText));
                media.query = query;
                media.obj = obj;
                media.loaded = false;
                //     media.onload = function () {
                //         images.queue.push(media);
                //console.log("New image load");
                //     }
                media.src = "http://{0}/{1}".format(window.location.host, obj["path"])
            }
        }
        xmlhttp.onerror = function () {
            failImageLoading();
        }

        xmlhttp.ontimeout = function () {
            failImageLoading();
        }

        if (images.dateQuery == null || images.dateQuery == "") {
            id = queue[queue.length - 1].obj['id'];

            query = "{0}?id={1}&media={2}&start={3}&end={4}".format(url, id, images.media,
                images.startDate, images.endDate);
        }
        else {
            query = "{0}?setdate={1}&media={2}&start={3}&end={4}".format(url, images.dateQuery,
                images.media, images.startDate, images.endDate);
            images.dateQuery = null;
        }

        xmlhttp.open("GET", query, true);
        xmlhttp.timeout = 10000;
        xmlhttp.send();
        //console.log("22. query={0} id={1} queue size={2}".format(query, id, queue.length));
    }
    /*
        function startSlideShow() {
            //images.slideShowID = setInterval(transitionSlides, images.slideDelay);
        } // startSlideShow
    */

    function failImageLoading() {
//        console.log("Fail to load images");
    }

    // start slide show
    function completeImagesLoading() {
//        console.log("succeed to load images. images.start %s", images.start);
        if (images.start == false) {
            images.start = true;
            transitionSlides();
        }
        else {
//            console.log("WARNING.  Already started");
        }
    }

    function adjustImage(img, winSize) {
        //console.log("Adjust image : %s x %s ", winSize.w, winSize.h);
        //console.log("Media size : %s x %s", img.clientWidth, img.clientHeight);

        if (img.clientHeight <= winSize.h && img.clientWidth <= winSize.w) {
            img.style.position = "absolute";
            img.style.left = (winSize.w - img.clientWidth) / 2 + "px";
            img.style.top = (winSize.h - img.clientHeight) / 2 + "px";

            // extend
            ratio = winSize.w / winSize.h;
            if (img.clientWidth / img.clientHeight > ratio) {
                // extend width.
                //console.log("extend width");
                width = winSize.w;
                height = img.clientHeight * width / img.clientWidth;
                img.style.left = 0 + "px";
                img.style.top = (winSize.h - height) / 2 + "px";

                img.style.width = width + "px";
                img.style.height = height + "px";

                //console.log("%f %f %f w=%s h=%s l=%s t=%s", height, img.clientHeight, height - img.clientHeight, img.style.width, img.style.height,
                //    img.style.left, img.style.top);
            }
            else {
                //console.log("extend hight");
                // extend hight
                height = winSize.h;
                width = img.clientWidth * height / img.clientHeight;

                img.style.left = (winSize.w - width) / 2 + "px";
                img.style.top = 0 + "px";

                img.style.width = width + "px";
                img.style.height = height + "px";

            }
            //console.log("size is smaller than canvas. ratio=%f", ratio);

            return;
        }

        var dh = img.clientHeight - winSize.h;
        var dw = img.clientWidth - winSize.w;

        var height = 0;
        var width = 0;

        // w : h = w.w : w.h
        if (dh > 0 && dw > 0) {
            if (dh >= dw) {
                height = winSize.h;
                width = img.clientWidth * winSize.h / img.clientHeight;
            }
            else {
                width = winSize.w;
                height = img.clientHeight * winSize.w / img.clientWidth;
            }
        }
        else {
            if (dh > 0) {
                height = winSize.h;
                width = img.clientWidth * winSize.h / img.clientHeight;
                //console.log("1." + height + ":" + width)
            }
            else {
                width = winSize.w;
                height = img.clientHeight * winSize.w / img.clientWidth;
                //console.log("2." + height + ":" + width)
            }
        }

        img.style.position = "absolute";
        img.style.height = height + "px";
        img.style.width = width + "px";
        img.style.left = (winSize.w - width) / 2 + "px";
        img.style.top = (winSize.h - height) / 2 + "px";

        //console.log("2." + width + ":" + height)
        //console.log("3." + img.style.top + ":" + img.style.left)
    }

    function getWindowSize() {
        var body = document.documentElement || document.body;

        return {
            w: window.innerWidth || body.clientWidth,
            h: window.innerHeight || body.clientHeight
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////

    function transitionSlides() {
        var nextMedia = images.queue[0];

        // if the same object is repeated over 3 tiems, skip it
        if (check_history(nextMedia.obj["id"]) == false) {
            // skip
            id = nextMedia.obj["id"];
            images.queue.shift();
            if (images.queue.length == 0) {
                images.start = false;
                var url = "http://{0}/{1}".format(window.location.host, images.url);
                fillImages(url, id, images.queue, images.maxQueueSize);

                return;
            }

            nextMedia = images.queue[0];
        }

        var nextMediaContainer = images.imageObjects[1 - images.curIndex];
        var mediaElement;

        if (nextMediaContainer.media_type == 'img') {
            mediaElement = nextMediaContainer.querySelectorAll('img')[0];
        }
        else {
            mediaElement = nextMediaContainer.querySelectorAll('video')[0];
        }

        var parent = mediaElement.parentNode;
        parent.removeChild(mediaElement);
        parent.insertBefore(nextMedia, parent.childNodes[0]);

        nextMediaContainer.media_type = nextMedia.type
        nextMediaContainer.obj = nextMedia.obj;
        nextMediaContainer.query = nextMedia.query;

        //elementImg.replaceWith(nextImage);
        // after replace, elementImg becomes invalid. refind it
        mediaElement = nextMediaContainer.querySelectorAll(nextMediaContainer.media_type)[0];
        adjustImage(mediaElement, { w: images.width, h: images.height });

        images.total += 1;

        if (images.debug) {
            images.imageDescObjects[1 - images.curIndex].innerHTML = nextMedia.obj["desc"] + " " + nextMedia.obj["id"] + " " + nextMedia.obj["path"] + " " + images.total;
        }
        else {
            images.imageDescObjects[1 - images.curIndex].innerHTML = nextMedia.obj["desc"];
        }

        var info_template = "\
        <span class=\"day\">\
            <span>\
                <canvas id=\"{0}_{4}\" class=\"skycon\" width=\"80px\" height=\"80px\"></canvas>\
            </span>\
            <div class =\"label\">\
                <div class =\"temp\">\
                    <span>{1}</span>\
                    <span class =\"unitwrap\">°F</span>\
                </div>\
                <span class =\"maxmin\">{2}°/{3}°</span>\
            </div>\
        </span>";

        weather = nextMedia.obj["weather"]
        //        weather["cur_icon"] = "wind";
        info = info_template.format(weather["icon"],
                                weather["cur_temperature"], weather["daily_max"], weather["daily_min"],
                                1 - images.curIndex);

        var ele = images.infoObjects[1 - images.curIndex];

        images.infoObjects[1 - images.curIndex].innerHTML = info;
        var icons = new Skycons({ color: "white" }),
            list = [
                "clear-day", "clear-night", "partly-cloudy-day",
                "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind",
                "fog"
            ],
            i;

        for (i = list.length; i--;)
            icons.set(list[i] + "_" + String(1 - images.curIndex), list[i]);

        icons.play();

        //        var scriptNode = document.createElement('script');
        //        scriptNode.innerHTML = info_script;
        //       images.infoObjects[1 - images.curIndex].appendChild(scriptNode);

        // get current image
        curMediaContainer = images.imageObjects[images.curIndex];

        if (curMediaContainer.obj == null) {
            cur_id = -1;
        }
        else {
            cur_id = curMediaContainer.obj["id"];
        }
   //     console.log("start transition cur=%s next=%s", cur_id, nextMediaContainer.obj["id"]);

        fadeTransition(curMediaContainer, nextMediaContainer);
    } // transitionSlides

    function fadeTransition(curMediaContainer, nextMediaContainer) {
        //console.log("start fade transition");

        var currentSlideOpacity = 1; // Fade the current slide out.
        var nextSlideOpacity = 0; // Fade the next slide in.
        var opacityLevelIncrement = 1 / 100;//images.fadeDelay;
        var fadeActiveSlidesID = setInterval(fadeActiveSlides, 100);
        var fadeout = 0.1; //10.0 * opacityLevelIncrement;
        var fadein = 0.1;//10.0 * opacityLevelIncrement;
        var fadeout = 10.0 * opacityLevelIncrement;
        var fadein = 10.0 * opacityLevelIncrement;

        function fadeActiveSlides() {
            var type = 1;

            if (type == 0) {
                if (currentSlideOpacity > 0) {
                    currentSlideOpacity -= fadeout;
                    curMediaContainer.style.opacity = currentSlideOpacity;
                }
                else if (nextSlideOpacity < 1) {
                    nextSlideOpacity += fadein;
                    nextMediaContainer.style.opacity = nextSlideOpacity;
                }
                else {
                    if (curMediaContainer.style)
                        curMediaContainer.style.opacity = 0;
                    nextMediaContainer.style.opacity = 1;
                    clearInterval(fadeActiveSlidesID);

                    completeTransition(curMediaContainer, nextMediaContainer);

                }
            }
            else {
                currentSlideOpacity -= fadeout;
                nextSlideOpacity += fadeout;

                if (currentSlideOpacity >= 0 && nextSlideOpacity <= 1) {
                    curMediaContainer.style.opacity = currentSlideOpacity;
                    nextMediaContainer.style.opacity = nextSlideOpacity;
                }
                else {
                    if (curMediaContainer.style)
                        curMediaContainer.style.opacity = 0;
                    nextMediaContainer.style.opacity = 1;
                    clearInterval(fadeActiveSlidesID);

                    completeTransition(curMediaContainer, nextMediaContainer);
                }
            }
            /*		
                    if (currentSlideOpacity >= 0 && nextSlideOpacity <= 1) {
                        curMediaContainer.style.opacity = currentSlideOpacity;
                        if (currentSlideOpacity <= 0.5)
                            nextMediaContainer.style.opacity = nextSlideOpacity;
                    //    nextMediaContainer.style.opacity = nextSlideOpacity;
                    }
                    else {
                        if (curMediaContainer.style)
                            curMediaContainer.style.opacity = 0;
                        nextMediaContainer.style.opacity = 1;
                        clearInterval(fadeActiveSlidesID);
        
                        completeTransition(curMediaContainer, nextMediaContainer);
                    }
                    */

        } // fadeActiveSlides
    }

    function completeTransition(curMediaContainer, nextMediaContainer) {

        obj = images.queue[0].obj
        //       createCookie(IMAGE_ID, obj["id"]);

        if (curMediaContainer.obj == null) {
            cur_id = -1;
        }
        else {
            cur_id = curMediaContainer.obj["id"];
        }
 //       console.log("complete transition  cur=%s next=%s", cur_id, nextMediaContainer.obj["id"]);

        // if settings are changed, save them
        if (images.slideDelay != parseInt(obj["slide_delay"])) {
            images.slideDelay = parseInt(obj["slide_delay"]);
            createCookie(SLIDE_DELAY, images.slideDelay);
            // console.log("slideDelay changes to " + images.slideDelay);
        }
        if (images.fadeDelay != parseInt(obj["fade_delay"])) {
            images.fadeDelay = parseInt(obj["fade_delay"]);
            createCookie(FADE_DELAY, images.fadeDelay);
            //console.log("fadeDelay changes to " + images.fadeDelay);
        }

        // clear old timer
        if (images.slideShowID != -1) {
            clearInterval(images.slideShowID);
            images.slideShowID = -1;
        }

        if (nextMediaContainer.media_type == 'video') {
            clearInterval(images.slideShowID);
            mediaElement = nextMediaContainer.querySelectorAll('video')[0];
            mediaElement.onended = function () {
   //             console.log("[%s] video Done =================== ", nextMediaContainer.obj["id"]);
                transitionSlides();
            }

            set_last_update(nextMediaContainer.obj["id"]);
            createCookie(IMAGE_ID, nextMediaContainer.obj["id"]);

            mediaElement.volume = images.videoVolume;
   //         console.log("[%s] start playing video. ", nextMediaContainer.obj["id"]);
            mediaElement.play();
            // start video
        }
        else {
            createCookie(IMAGE_ID, nextMediaContainer.obj["id"]);
            set_last_update(nextMediaContainer.obj["id"]);
            // if pic, start new timer
  //          console.log("start new timer. delay" + images.slideDelay);
            images.slideShowID = setInterval(transitionSlides, images.slideDelay);
        }
  //      console.log("media.query=%s", nextMediaContainer.query);
        createCookie(QUERY, nextMediaContainer.query);

        images.queue.shift();
        images.curIndex = 1 - images.curIndex;
        //console.log(nextMediaContainer.obj)
        var url = "http://{0}/{1}".format(window.location.host, images.url);
        //fillOneImage(url, images.queue);

        id = images.queue[images.queue.length - 1].obj['id'];
        fillImages(url, id, images.queue, images.maxQueueSize);
    }

} // slideShow

function onConfig() {
    // Get the modal
    var modal = document.getElementById('myModal');

    // Get the button that opens the modal
    var btn = document.getElementById("myBtn");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    // When the user clicks the button, open the modal
    btn.onclick = function () {
        modal.style.display = "block";
        //document.config.volume.value = readCookie(VIDEO_VOLUME, "1");

        if ((navigator.userAgent.indexOf("MSIE") != -1) || (!!document.documentMode == true)) //IF IE > 10
        {   /*
            var today = new Date();
            var dd = today.getDate();

            var mm = today.getMonth() + 1;
            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd;
            }

            if (mm < 10) {
                mm = '0' + mm;
            }
            document.config.start.value = mm + '/' + dd + '/' + yyyy;
            */
            // 01234567890
            // 2013-05-16   ->   05/16/2013
            s = images.startDate;
 //           alert(s);
            document.config.start.value = s.substring(5, 7) + '/' + s.substring(8) + '/' + s.substring(0, 4)
            s = images.endDate;
            document.config.end.value = s.substring(5, 7) + '/' + s.substring(8) + '/' + s.substring(0, 4)

        }
        else {
            document.config.start.value = images.startDate;
            document.config.end.value = images.endDate;
        }

        document.config.setDate.value = "none";

        for (i = 0; i < document.config.media.length; i++) {
            if (document.config.media[i].value == images.media) {
                document.config.media[i].checked = true;
                break;
            }
        }
        // document.config.media.value = images.media;
        
        document.config.debug.checked = images.debug;
        document.config.volume.value = images.videoVolume * 100;
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

}

function onSave() {
    var media = document.config.media;

    if (document.config.setDate.value && document.config.setDate.value != "none") {
        images.dateQuery = document.config.setDate.value;
        if ((navigator.userAgent.indexOf("MSIE") != -1) || (!!document.documentMode == true)) //IF IE > 10
        {   // 0123456789
            // 05/16/2013
            s = document.config.setDate.value;
            images.dateQuery = s.substring(6) + "-" + s.substring(0, 2) + "-" + s.substring(3, 5);
            alert(images.dateQuery);
        }
        createCookie(SET_DATE, images.dateQuery);
        eraseCookie(QUERY);
    }

    if (document.config.start.value && document.config.start.value != "none") {
        images.startDate = document.config.start.value;
        if ((navigator.userAgent.indexOf("MSIE") != -1) || (!!document.documentMode == true)) //IF IE > 10
        {   // 0123456789
            // 05/16/2013
            s = document.config.start.value;
            images.startDate = s.substring(6) + "-" + s.substring(0, 2) + "-" + s.substring(3, 5);
//            alert(images.startDate + "," + images.endDate);
        }
    }
    else {
        images.startDate = DEFAULT_START_DATE;
    }

    if (document.config.end.value && document.config.end.value != "none") {
        images.endDate = document.config.end.value;
        if ((navigator.userAgent.indexOf("MSIE") != -1) || (!!document.documentMode == true)) //IF IE > 10
        {   // 0123456789
            // 05/16/2013
            s = document.config.end.value;
            images.endDate = s.substring(6) + "-" + s.substring(0, 2) + "-" + s.substring(3, 5);
            alert(images.startDate + "," + images.endDate);
        }
    }
    else {
        images.endDate = DEFAULT_END_DATE;
    }

    if (images.startDate > images.endDate) {
        images.startDate = DEFAULT_START_DATE;
        images.endDate = DEFAULT_END_DATE;

        alert("wrong date setting. reset");
    }
    createCookie(START_DATE, images.startDate);
    createCookie(END_DATE, images.endDate);
    eraseCookie(QUERY);

    vol = document.config.volume.value / 100.0;
    images.videoVolume = vol;

    var media;
    for (i = 0; i < document.config.media.length; i++) {
        if (document.config.media[i].checked) {
            media = document.config.media[i].value;
            break;
        }
    }

    if (media != images.media) {
        eraseCookie(QUERY);
    }

    images.media = media;

    images.debug = document.config.debug.checked;

    createCookie(DEBUG, images.debug);
    createCookie(MEDIA, images.media);
    createCookie(VIDEO_VOLUME, images.videoVolume);

    var modal = document.getElementById('myModal');
    modal.style.display = "none";
    location.reload();

    return false;
}