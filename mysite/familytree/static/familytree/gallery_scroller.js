// Simple gallery scroller for Django/Hotwire thumbnail row
// Assumes thumbnails are in a div with id 'gallery-thumbnails' and each thumb has class 'gallery-thumb'
// Currently shows 10 thumbnails per row; adjust maxVisible below to change this
(function(){
    var maxVisible = 10; // number of thumbnails to show per row
    var startIdx = 0;
    function renderGallery(resetIdx){
        if (resetIdx) startIdx = 0;
        var thumbs = document.querySelectorAll('#gallery-thumbnails .gallery-thumb');
        thumbs.forEach(function(el, i){
            el.style.display = (i >= startIdx && i < startIdx+maxVisible) ? '' : 'none';
        });
        // Show/hide right arrow
        var arrowR = document.getElementById('gallery-arrow-right');
        if(arrowR) arrowR.style.display = (startIdx+maxVisible < thumbs.length) ? '' : 'none';
        // Show/hide left arrow
        var arrowL = document.getElementById('gallery-arrow-left');
        if(arrowL) arrowL.style.display = (startIdx > 0) ? '' : 'none';
    }
    window.galleryNext = function(){
        var thumbs = document.querySelectorAll('#gallery-thumbnails .gallery-thumb');
        if(startIdx+maxVisible < thumbs.length){
            startIdx += maxVisible;
            if(startIdx > thumbs.length-maxVisible) startIdx = thumbs.length-maxVisible;
            renderGallery();
        }
    };
    window.galleryPrev = function(){
        if(startIdx > 0){
            startIdx -= maxVisible;
            if(startIdx < 0) startIdx = 0;
            renderGallery();
        }
    };
    document.addEventListener('DOMContentLoaded', function(){ renderGallery(true); });
    window.addEventListener('turbo:frame-load', function(){ renderGallery(true); });
    window.addEventListener('turbo:load', function(){ renderGallery(true); });
})();
