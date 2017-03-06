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
        slideDelay: 4000, // The time interval between consecutive slides.
        fadeDelay: 35, // The time interval between individual opacity changes. This should always be much smaller than slideDelay.  
        wrapperID: "slideShowImages", // The ID of the <div> element that contains all of the <img> elements to be shown as a slide show.
        wrapperObject: null, // Will contain a reference to the <div> element that contains all of the <img> elements to be shown as a slide show.

        slideShowID: null, // A setInterval() ID value used to stop the slide show.
        slideShowRunning: true, // Used to record when the slide show is running and when it's not. The slide show is always initially running.    
        slideIndex: 0, // The index of the current slide image.

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

    id = readCookie(IMAGE_ID, -1);
    fillImages(images.url, id, images.queue, images.maxQueueSize);

    return;

    function completeImagesLoading() {
        console.log("succeed to load images");
        // Hide the not needed <div> wrapper element.
       // images.wrapperObject.style.display = "none"; 

        size = getWindowSize();
        var slideWidthMax = size.w; // Returns a value that is always in pixel units.
        var slideHeightMax = size.h; // Returns a value that is always in pixel units.

        images.wrapperObject.style.position = "relative";
        images.wrapperObject.style.overflow = "hidden"; // This is just a safety thing.
        images.wrapperObject.style.width = slideWidthMax + "px";
        images.wrapperObject.style.height = slideHeightMax + "px";

        newImage = images.queue[0];
        
        resizeImage(newImage, size);
        console.log(size);
        console.log(newImage);
        imageId = "slideimage" + images.curIndex;
        img1 = document.getElementById(imageId);
        images.queue[0].id = imageId;
        img1.replaceWith(newImage);
        
        images.curIndex = 1 - images.curIndex;
    }

    function failImageLoading() {
        console.log("Fail to load images");
    }

    function resizeImage(img, winSize) {
        if (newImage.height <= winSize.h && newImage.weight <= winSize.w) {
            console.log("enought");
            return;
        }

        dh = newImage.height - winSize.h;
        dw = newImage.width - winSize.w;

        // w : h = w.w : w.h
        if (dh > 0 && dw > 0) {
            if (dh >= dw) {
                newImage.style.height = winSize.h + "px";
                newImage.style.width = newImage.width * winSize.h / newImage.height + "px";
            }
            else {
                newImage.style.width = winSize.w + "px";
                newImage.style.height = newImage.height * winSize.w / newImage.width + "px";
            }
            return;
        }

        if (dh > 0) {
            newImage.style.height = winSize.h + "px";
            newImage.style.width = newImage.width * winSize.h / newImage.height + "px";
        }
        else {
            newImage.style.width = winSize.w; + "px";
            newImage.style.height = newImage.height * winSize.w / newImage.width + "px";
        }
    }

    function getWindowSize() {
        var body = document.documentElement || document.body;

        return {
            w: window.innerWidth || body.clientWidth,
            h: window.innerHeight || body.clientHeight
        }
    }
   // initializeSlideShowMarkup();
   // startSlideShow();

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

        console.log("1. url={0} id={1} queue size={2}".format(url, id, queue.length));

        xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                obj = JSON.parse(xmlhttp.responseText);

                console.log("3. url={0} id={1} obj={2}".format(url, id, xmlhttp.responseText));
                var image = new Image();
                image.obj = obj;
                image.onload = function () {
                    images.queue.push(image);
                    console.log("4. id={0} queue size={1}".format(obj['id'], queue.length));
                    fillImages(url, obj['id'], queue, maxQueueSize);
                }
                image.src = "http://{0}/{1}".format(window.location.host, obj["path"])
            }
        }
        xmlhttp.onerror = function () {
            failImageLoading();
        }

        xmlhttp.ontimeout = function() {
            failImageLoading();
        }

        query = "{0}?id={1}".format(url, id);
        xmlhttp.open("GET", query, true);
        xmlhttp.timeout = 10000;
        xmlhttp.send();
        console.log("2. query={0} id={1} queue size={2}".format(query, id, queue.length));
    }

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function initializeSlideShowMarkup() {
        var slideWidthMax = maxSlideWidth(); // Returns a value that is always in pixel units.
        var slideHeightMax = maxSlideHeight(); // Returns a value that is always in pixel units.

        images.wrapperObject.style.position = "relative";
        images.wrapperObject.style.overflow = "hidden"; // This is just a safety thing.
        images.wrapperObject.style.width = slideWidthMax + "px";
        images.wrapperObject.style.height = slideHeightMax + "px";

        var slideCount = globals.slideImages.length;
        for (var i = 0; i < slideCount; i++) {
            globals.slideImages[i].style.opacity = 0;
            globals.slideImages[i].style.position = "absolute";
            globals.slideImages[i].style.top = (slideHeightMax - globals.slideImages[i].getBoundingClientRect().height) / 2 + "px";
            globals.slideImages[i].style.left = (slideWidthMax - globals.slideImages[i].getBoundingClientRect().width) / 2 + "px";
        }

        globals.slideImages[0].style.opacity = 1; // Make the first slide visible.

        if (globals.buttonObject) {
            globals.buttonObject.textContent = globals.buttonStopText;
        }
    } // initializeSlideShowMarkup

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function maxSlideWidth() {
        var maxWidth = 0;
        var maxSlideIndex = 0;
        var slideCount = globals.slideImages.length;

        for (var i = 0; i < slideCount; i++) {
            if (globals.slideImages[i].width > maxWidth) {
                maxWidth = globals.slideImages[i].width; // The width of the widest slide so far.
                maxSlideIndex = i; // The slide with the widest width so far.
            }
        }

        return globals.slideImages[maxSlideIndex].getBoundingClientRect().width; // Account for the image's border, padding, and margin values. Note that getBoundingClientRect() is always in units of pixels.
    } // maxSlideWidth

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function maxSlideHeight() {
        var maxHeight = 0;
        var maxSlideIndex = 0;
        var slideCount = globals.slideImages.length;

        for (var i = 0; i < slideCount; i++) {
            if (globals.slideImages[i].height > maxHeight) {
                maxHeight = globals.slideImages[i].height; // The height of the tallest slide so far.
                maxSlideIndex = i; // The slide with the tallest height so far.
            }
        }

        return globals.slideImages[maxSlideIndex].getBoundingClientRect().height; // Account for the image's border, padding, and margin values. Note that getBoundingClientRect() is always in units of pixels.
    } // maxSlideHeight

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function startSlideShow() {
        globals.slideShowID = setInterval(transitionSlides, globals.slideDelay);
    } // startSlideShow

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function haltSlideShow() {
        clearInterval(globals.slideShowID);
    } // haltSlideShow

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function toggleSlideShow() {
        if (globals.slideShowRunning) {
            haltSlideShow();
            if (globals.buttonObject) {
                globals.buttonObject.textContent = globals.buttonStartText;
            }
        }
        else {
            startSlideShow();
            if (globals.buttonObject) {
                globals.buttonObject.textContent = globals.buttonStopText;
            }
        }
        globals.slideShowRunning = !(globals.slideShowRunning);
    } // toggleSlideShow

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function transitionSlides() {
        cur_image = globals.image_queue.shift();
        next_image = globals.image_queue[0];

        var currentSlideOpacity = 1; // Fade the current slide out.
        var nextSlideOpacity = 0; // Fade the next slide in.
        var opacityLevelIncrement = 1 / globals.fadeDelay;
        var fadeActiveSlidesID = setInterval(fadeActiveSlides, globals.fadeDelay);

        function fadeActiveSlides() {
            currentSlideOpacity -= opacityLevelIncrement;
            nextSlideOpacity += opacityLevelIncrement;

            // console.log(currentSlideOpacity + nextSlideOpacity); // This should always be very close to 1.

            if (currentSlideOpacity >= 0 && nextSlideOpacity <= 1) {
                cur_image.style.opacity = currentSlideOpacity;
                next_image.style.opacity = nextSlideOpacity;
            }
            else {
                cur_image.style.opacity = 0;
                next_image.style.opacity = 1;
                clearInterval(fadeActiveSlidesID);

                get_next_image(globals.image_queue);
            }
        } // fadeActiveSlides
    } // transitionSlides



} // slideShow


/*
function preload(url, timeout) {
    this.canceltimeout = function () {
        clearTimeout(this.timeout);
        this.loaded = true;
        return false;
    }

    this.abort = function () {
        this.xhr.abort();
        this.aborted = true;
    }

    //creates a closure to bind the functions to the right execution scope
    this.$_bind = function (method) {
        var obj = this;
        return function (e) { obj[method](e); };
    }

    //set a default of 10 second timeout
    if (timeout == null) {
        timeout = 10000;
    }

    this.aborted = false;
    this.loaded = false;
    this.xhr = new XMLHttpRequest();
    this.xhr.onreadystatechange = this.$_bind('canceltimeout');
    this.xhr.open('GET', url);
    this.xhr.send('');
    this.timeout = setTimeout(this.$_bind('abort'), timeout);
}


// http://blog.teamtreehouse.com/learn-asynchronous-image-loading-javascript
function download() {
    var image = document.images[0];
    var downloadingImage = new Image();
    downloadingImage.onload = function () {
        image.src = this.src;
    };
    downloadingImage.src = "http://an.image/to/aynchrounously/download.jpg";

}

// https://www.sitepoint.com/preloading-images-in-parallel-with-promises/


document.body.style.overflow = 'hidden';





var llama = new preload('media/1.jpg');
console.log(llama)
show_image();


function resize(img) {
    winDim = getWinDim();


    img.style.height = winDim.y - 00 + "px";

    if (img.offsetWidth > winDim.x) {
        img.style.height = null;
        img.style.width = winDim.x + "px";
    }
}

function getWinDim() {
    var body = document.documentElement || document.body;

    return {
        x: window.innerWidth || body.clientWidth,
        y: window.innerHeight || body.clientHeight
    }
}

function show_image() {
    if (llama.loaded) {
        var l = new Image();
        l.src = 'media/1.jpg';
        resize(l);
        document.body.appendChild(l);
    } else if (llama.aborted) {
        var l = document.createElement('p');
        l.innerHTML = 'image.gif got cancelled';
        document.body.appendChild(l);
    } else {
        setTimeout(show_image, 10);
    }
    return false;
}


*/
