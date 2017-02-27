//window.addEventListener('load', slideShow, false);

function slideShow() {

    /* GLOBALS **********************************************************************************************/

    var globals = {
        slideDelay: 4000, // The time interval between consecutive slides.
        fadeDelay: 35, // The time interval between individual opacity changes. This should always be much smaller than slideDelay.  
        wrapperID: "slideShowImages", // The ID of the <div> element that contains all of the <img> elements to be shown as a slide show.
        buttonID: "slideShowButton", // The ID of the <button> element that toggles the slide show on and off.
        buttonStartText: "Start Slides", // Text used in the slide show toggle button.
        buttonStopText: "Stop Slides", // Text used in the slide show toggle button.    
        wrapperObject: null, // Will contain a reference to the <div> element that contains all of the <img> elements to be shown as a slide show.
        buttonObject: null, // If present, will contain a reference to the <button> element that toggles the slide show on and off. The initial assumption is that there is no such button element (hence the false value).
        slideImages: [], // Will contain all of the slide image objects.
        slideShowID: null, // A setInterval() ID value used to stop the slide show.
        slideShowRunning: true, // Used to record when the slide show is running and when it's not. The slide show is always initially running.    
        slideIndex: 0 // The index of the current slide image.
    }

    /* MAIN *************************************************************************************************/

    initializeGlobals();

    if (insufficientSlideShowMarkup()) {
        return; // Insufficient slide show markup - exit now.
    }

    // Assert: there's at least one slide image.

   // if (globals.slideImages.length == 1) {
   //     return; // The solo slide image is already being displayed - exit now.
   // }

    // Assert: there's at least two slide images.

    initializeSlideShowMarkup();

    globals.wrapperObject.addEventListener('click', toggleSlideShow, false); // If the user clicks a slide show image, it toggles the slide show on and off.

    if (globals.buttonObject) {
        globals.buttonObject.addEventListener('click', toggleSlideShow, false); // This callback is used to toggle the slide show on and off.
    }

    startSlideShow();

    /* FUNCTIONS ********************************************************************************************/

    function initializeGlobals() {
        globals.wrapperObject = (document.getElementById(globals.wrapperID) ? document.getElementById(globals.wrapperID) : null);
        globals.buttonObject = (document.getElementById(globals.buttonID) ? document.getElementById(globals.buttonID) : null);

        if (globals.wrapperObject) {
            globals.slideImages = (globals.wrapperObject.querySelectorAll('img') ? globals.wrapperObject.querySelectorAll('img') : []);
        }
    } // initializeGlobals

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function insufficientSlideShowMarkup() {
        if (!globals.wrapperObject) { // There is no wrapper element whose ID is globals.wrapperID - fatal error.
            if (globals.buttonObject) {
                globals.buttonObject.style.display = "none"; // Hide the not needed slide show button element when present.
            }
            return true;
        }

        if (!globals.slideImages.length) { // There needs to be at least one slide <img> element - fatal error.
            if (globals.wrapperObject) {
                globals.wrapperObject.style.display = "none"; // Hide the not needed <div> wrapper element.
            }

            if (globals.buttonObject) {
                globals.buttonObject.style.display = "none"; // Hide the not needed slide show button element.
            }

            return true;
        }

        return false; // The markup expected by this library seems to be present.
    } // insufficientSlideShowMarkup

    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    function initializeSlideShowMarkup() {
        var slideWidthMax = maxSlideWidth(); // Returns a value that is always in pixel units.
        var slideHeightMax = maxSlideHeight(); // Returns a value that is always in pixel units.

        globals.wrapperObject.style.position = "relative";
        globals.wrapperObject.style.overflow = "hidden"; // This is just a safety thing.
        globals.wrapperObject.style.width = slideWidthMax + "px";
        globals.wrapperObject.style.height = slideHeightMax + "px";

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
        var currentSlide = globals.slideImages[globals.slideIndex];

        ++(globals.slideIndex);
        if (globals.slideIndex >= globals.slideImages.length) {
            globals.slideIndex = 0;
        }

        var nextSlide = globals.slideImages[globals.slideIndex];

        var currentSlideOpacity = 1; // Fade the current slide out.
        var nextSlideOpacity = 0; // Fade the next slide in.
        var opacityLevelIncrement = 1 / globals.fadeDelay;
        var fadeActiveSlidesID = setInterval(fadeActiveSlides, globals.fadeDelay);

        function fadeActiveSlides() {
            currentSlideOpacity -= opacityLevelIncrement;
            nextSlideOpacity += opacityLevelIncrement;

            // console.log(currentSlideOpacity + nextSlideOpacity); // This should always be very close to 1.

            if (currentSlideOpacity >= 0 && nextSlideOpacity <= 1) {
                currentSlide.style.opacity = currentSlideOpacity;
                nextSlide.style.opacity = nextSlideOpacity;
            }
            else {
                currentSlide.style.opacity = 0;
                nextSlide.style.opacity = 1;
                clearInterval(fadeActiveSlidesID);
            }
        } // fadeActiveSlides
    } // transitionSlides

    function process() {
        old_image = image_queue.shift();
        new_image = image_queue[0];
        transitionSlides(image_queue);
        
        load_new_image(image_queue)
    }
} // slideShow

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
