/*
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
SLIDE_DELAY = "slideDelay"
FADE_DELAY = "fadeDelay"
IMAGE1 = "slideimage0";
IMAGE2 = "slideimage1";

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

function slideShow() {

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
        width: 0,
        height: 0,
        queue: [],
        curIndex: 1,
        maxQueueSize: 3,
        url: "nextimage"
    }

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
        desc.style.top = (size.h - 100) + "px";
        desc.style.left = 10 + "px";
    }

 //   console.log(images.descObject);
    console.log("READ COOKIE");
    var id = readCookie(IMAGE_ID, -1);
    id = -1;
    images.slideDelay = readCookie(SLIDE_DELAY, images.slideDelay)
    images.fadeDelay = readCookie(FADE_DELAY, images.fadeDelay)
    var url = "http://{0}/{1}".format(window.location.host, images.url);

    console.log("slideDelay=" + images.slideDelay + " fadeDelay=" + images.fadeDelay + " url=" + url);
    fillImages(url, id, images.queue, images.maxQueueSize);

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

    function fillImages(url, id, queue, maxQueueSize) {
        if (queue.length >= maxQueueSize) {
            completeImagesLoading();
            return;
        }

        //console.log("1. url={0} id={1} queue size={2}".format(url, id, queue.length));

        xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                function finish_load() {
                    images.queue.push(media);
                    console.log("4. id={0} queue size={1}".format(obj['id'], queue.length));
                    fillImages(url, obj['id'], queue, maxQueueSize);
                }

                obj = JSON.parse(xmlhttp.responseText);

                console.log("3. url={0} id={1} obj={2}".format(url, id, xmlhttp.responseText));

                if (obj["media_type"] == 'img') {
                    media = new Image();
                    media.type = "img";
                    console.log("load img");
                    media.onload = function () {
                        finish_load();
                    }
                }
                else if (obj["media_type"] == 'video') {
                    media = document.createElement('video');
                    media.type = "video";
                    console.log("load video");

                    // https://www.w3schools.com/tags/av_event_canplay.asp
                    media.oncanplay = function () {
                        finish_load();
                    }
                }
                else {
                    alert("invalid format=" + obj["media_type"]);
                    return;
                }

                // new Image() vs document.createElement('img')
                // https://stackoverflow.com/questions/6241716/is-there-a-difference-between-new-image-and-document-createelementimg
                
                media.obj = obj;
                media.src = "http://{0}/{1}".format(window.location.host, obj["path"])
                console.log("media.src " + media.src);
            }
        }
        xmlhttp.onerror = function () {
            failImageLoading();
        }

        xmlhttp.ontimeout = function () {
            failImageLoading();
        }

        query = "{0}?id={1}".format(url, id);
        xmlhttp.open("GET", query, true);
        xmlhttp.timeout = 10000;
        xmlhttp.send();
        //console.log("2. query={0} id={1} queue size={2}".format(query, id, queue.length));
    }

    function fillOneImage(url, queue) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                obj = JSON.parse(xmlhttp.responseText);

                console.log("{0}", obj);
                if (obj["media_type"] == 'img') {
                    media = new Image();
                    media.type = "img";
                    console.log("load img 1");
                    media.onload = function () {
                        images.queue.push(media);
                    }
                }
                else if (obj["media_type"] == 'video') {
                    media = document.createElement('video')
                    media.type = "video";

                    console.log("load video 1");
                    media.oncanplay = function () {
                        images.queue.push(media);
                    }
                }
                else {
                    alert("invalid format=" + obj["type"]);
                    return;
                }

                //console.log("3. url={0} id={1} obj={2}".format(url, id, xmlhttp.responseText));
                media.obj = obj;
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

        id = queue[queue.length - 1].obj['id'];

        query = "{0}?id={1}".format(url, id);
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
        console.log("Fail to load images");
    }

    // start slide show
    function completeImagesLoading() {
        console.log("succeed to load images");
        transitionSlides();
    }

    function adjustImage(img, winSize) {
        console.log("Adjust image : %s x %s ", winSize.w, winSize.h);
        console.log("Media size : %s x %s", img.clientWidth, img.clientHeight);

        if (img.clientHeight <= winSize.h && img.clientWidth <= winSize.w) {
            img.style.position = "absolute";
            img.style.left = (winSize.w - img.clientWidth) / 2 + "px";
            img.style.top = (winSize.h - img.clientHeight) / 2 + "px";

            // extend
            ratio = winSize.w / winSize.h;
            if (img.clientWidth / img.clientHeight > ratio) {
                // extend width.
                console.log("extend width");
                width = winSize.w; 
                height = img.clientHeight * width / img.clientWidth;
                img.style.left = 0 + "px";
                img.style.top = (winSize.h - height) / 2 + "px";

                img.style.width = width + "px";
                img.style.height = height + "px";

                console.log("%f %f %f w=%s h=%s l=%s t=%s", height, img.clientHeight, height - img.clientHeight, img.style.width, img.style.height,
                    img.style.left, img.style.top);
            }
            else {
                console.log("extend hight");
                // extend hight
                height = winSize.h;
                width = img.clientWidth * height / img.clientHeight;

                img.style.left = (winSize.w - width) / 2 + "px";
                img.style.top = 0 + "px";

                img.style.width = width + "px";
                img.style.height = height + "px";

            }
            console.log("size is smaller than canvas. ratio=%f", ratio);

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
                console.log("1." + height + ":" + width)
            }
            else {
                width = winSize.w;
                height = img.clientHeight * winSize.w / img.clientWidth;
                console.log("2." + height + ":" + width)
            }
        }

        img.style.position = "absolute";
        img.style.height = height + "px";
        img.style.width = width + "px";
        img.style.left = (winSize.w - width) / 2 + "px";
        img.style.top = (winSize.h - height) / 2 + "px";

        //console.log("2." + width + ":" + height)
        console.log("3." + img.style.top + ":" + img.style.left)
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
        console.log("start transition slide");
        var nextMedia = images.queue[0];
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

        //elementImg.replaceWith(nextImage);
        // after replace, elementImg becomes invalid. refind it
        mediaElement = nextMediaContainer.querySelectorAll(nextMediaContainer.media_type)[0];
        adjustImage(mediaElement, { w: images.width, h: images.height } );

        images.imageDescObjects[1 - images.curIndex].innerHTML = nextMedia.obj["desc"]

        // get current image
        curMediaContainer = images.imageObjects[images.curIndex];

        fadeTransition(curMediaContainer, nextMediaContainer);
    } // transitionSlides

    function fadeTransition(curMediaContainer, nextMediaContainer) {
        console.log("start fade transition");

        var currentSlideOpacity = 1; // Fade the current slide out.
        var nextSlideOpacity = 0; // Fade the next slide in.
        var opacityLevelIncrement = 1 / images.fadeDelay;
        var fadeActiveSlidesID = setInterval(fadeActiveSlides, images.fadeDelay);

        function fadeActiveSlides() {
            currentSlideOpacity -= opacityLevelIncrement;
            nextSlideOpacity += opacityLevelIncrement;

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
        } // fadeActiveSlides
    }

    function completeTransition(curMediaContainer, nextMediaContainer) {
        console.log("complete transition");

        obj = images.queue[0].obj
        createCookie(IMAGE_ID, obj["id"]);

        // if settings are changed, save them
        if (images.slideDelay != parseInt(obj["slide_delay"])) {
            images.slideDelay = parseInt(obj["slide_delay"]);
            createCookie(SLIDE_DELAY, images.slideDelay);
            console.log("slideDelay changes to " + images.slideDelay);
        }
        if (images.fadeDelay != parseInt(obj["fade_delay"])) {
            images.fadeDelay = parseInt(obj["fade_delay"]);
            createCookie(FADE_DELAY, images.fadeDelay);
            console.log("fadeDelay changes to " + images.fadeDelay);
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
                console.log("video is ended.  notify");
                transitionSlides();
            }

            console.log("start playing video");
            mediaElement.play();
            // start video
        }
        else {
            // if pic, start new timer
            console.log("start new timer. delay" + images.slideDelay);
            images.slideShowID = setInterval(transitionSlides, images.slideDelay);
        }

        images.queue.shift();
        images.curIndex = 1 - images.curIndex;
        //console.log(nextMediaContainer.obj)
        var url = "http://{0}/{1}".format(window.location.host, images.url);
        fillOneImage(url, images.queue);
    }

} // slideShow

