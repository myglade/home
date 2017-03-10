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

function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else
        expires = "";

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


window.addEventListener('load', slideShow, false);

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

        slideShowID: null, // A setInterval() ID value used to stop the slide show.
        slideShowRunning: true, // Used to record when the slide show is running and when it's not. The slide show is always initially running.    

        width: 0,
        height: 0,
        queue: [],
        curIndex: 1,
        maxQueueSize: 3,
        url: "http://localhost:5000/nextimage"
    }

    /* MAIN *************************************************************************************************/

    if (!document.getElementById(images.wrapperID))
        return;

    images.wrapperObject = document.getElementById(images.wrapperID);
    if (!images.wrapperObject)
        return;

    document.body.style.overflow = 'hidden';
    id = readCookie(IMAGE_ID, -1);
    fillImages(images.url, id, images.queue, images.maxQueueSize);

    return;

    /* FUNCTIONS ********************************************************************************************/
    /*
    {
      "address": "Not Found",
      "created": "2015:12:11 15:26:20",
      "id": 6,
      "loc": null,
      "name": "6.jpg",
      "path": "media/6.jpg"
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
                obj = JSON.parse(xmlhttp.responseText);

                //console.log("3. url={0} id={1} obj={2}".format(url, id, xmlhttp.responseText));
                var image = new Image();
                image.obj = obj;
                image.onload = function () {
                    images.queue.push(image);
                    //console.log("4. id={0} queue size={1}".format(obj['id'], queue.length));
                    fillImages(url, obj['id'], queue, maxQueueSize);
                }
                image.src = "http://{0}/{1}".format(window.location.host, obj["path"])
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
        xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                obj = JSON.parse(xmlhttp.responseText);

                //console.log("3. url={0} id={1} obj={2}".format(url, id, xmlhttp.responseText));
                var image = new Image();
                image.obj = obj;
                image.onload = function () {
                    images.queue.push(image);
                    //console.log("New image load");
                }
                image.src = "http://{0}/{1}".format(window.location.host, obj["path"])
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

    function startSlideShow() {
        images.slideShowID = setInterval(transitionSlides, images.slideDelay);
    } // startSlideShow

    function failImageLoading() {
        console.log("Fail to load images");
    }

    function completeImagesLoading() {
        console.log("succeed to load images");
        // Hide the not needed <div> wrapper element.
        //images.wrapperObject.style.display = "none"; 

        size = getWindowSize();
        images.width = size.w; // Returns a value that is always in pixel units.
        images.height = size.h; // Returns a value that is always in pixel units.

        images.wrapperObject.style.position = "absolute";
        images.wrapperObject.style.overflow = "hidden"; // This is just a safety thing.
        images.wrapperObject.style.width = images.width + "px";
        images.wrapperObject.style.height = images.height + "px";
        images.wrapperObject.style.top = 0;
        images.wrapperObject.style.left = 0;

        //console.log("1." + size.w + ":" + size.h)
        startSlideShow();
    }

    function adjustImage(img, winSize) {
        if (img.height <= winSize.h && img.width <= winSize.w) {
            console.log("size is smaller than canvas");
            return;
        }

        dh = img.height - winSize.h;
        dw = img.width - winSize.w;

        height = 0;
        width = 0;

        // w : h = w.w : w.h
        if (dh > 0 && dw > 0) {
            if (dh >= dw) {
                height = winSize.h;
                width = img.width * winSize.h / img.height;
            }
            else {
                width = winSize.w;
                height = img.height * winSize.w / img.width;
            }
        }
        else {
            if (dh > 0) {
                height = winSize.h;
                width = img.width * winSize.h / img.height;
            }
            else {
                width = winSize.w;
                height = img.height * winSize.w / img.width;
            }
        }

        nextImage.style.opacity = 0;
        img.style.position = "absolute";
        img.style.height = height + "px";
        img.style.width = width + "px";
        img.style.left = (images.width - width) / 2 + "px";
        img.style.top = (images.height - height) / 2 + "px";

        //console.log("2." + width + ":" + height)
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
        nextImage = images.queue[0];
        adjustImage(nextImage, size);

        nextImageId = "slideimage" + (1 - images.curIndex);
        nextImageElement = document.getElementById(nextImageId);
        if (!nextImageElement) {
            console.log("next image is NULL");
            return;
        }

        nextImage.id = nextImageId;
        nextImageElement.replaceWith(nextImage);
        // after replace, ele should be obtained again
        nextImageElement = document.getElementById(nextImageId);

        // get current image
        curImageId = "slideimage" + images.curIndex;
        curImageElement = document.getElementById(curImageId);
        if (!curImageElement) {
            console.log("curImageElement is NULL");
            window.location.reload(false); 
            return;
        }

        images.curIndex = 1 - images.curIndex;
        fadeTransition(curImageElement, nextImageElement);
    } // transitionSlides

    function fadeTransition(curImageElement, nextImageElement) {
        var currentSlideOpacity = 1; // Fade the current slide out.
        var nextSlideOpacity = 0; // Fade the next slide in.
        var opacityLevelIncrement = 1 / images.fadeDelay;
        var fadeActiveSlidesID = setInterval(fadeActiveSlides, images.fadeDelay);

        function fadeActiveSlides() {
            currentSlideOpacity -= opacityLevelIncrement;
            nextSlideOpacity += opacityLevelIncrement;

            if (currentSlideOpacity >= 0 && nextSlideOpacity <= 1) {
                curImageElement.style.opacity = currentSlideOpacity;
                nextImageElement.style.opacity = nextSlideOpacity;
            }
            else {
                if (curImageElement.style)
                    curImageElement.style.opacity = 0;
                nextImageElement.style.opacity = 1;
                clearInterval(fadeActiveSlidesID);

                if (curImageElement.obj)
                    createCookie(IMAGE_ID, curImageElement.obj["id"]);
                else
                    createCookie(IMAGE_ID, -1);

                images.queue.shift();
                fillOneImage(images.url, images.queue);
            }
        } // fadeActiveSlides
    }

} // slideShow

