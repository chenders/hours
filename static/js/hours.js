// First, checks if it isn't implemented yet.
if (!String.prototype.format) {
    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}

function getURLP(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null;
}
var headerHeights = [];
function updateHeaderDate() {
    scrollHeight = $(document).scrollTop();
    headerIdx = 0;
    for (headerIdx = 0; scrollHeight > headerHeights[headerIdx]; headerIdx++);
    $('#current-date').html($('th:eq(' + ((headerIdx == 0 ? headerIdx : headerIdx - 1)) + ')').text());
}

$(document).ready(function() {
    var optionHtml = $('#date-select option').remove()[0].outerHTML;
    $.each(hours.dates, function() {
        $('#date-select').append(optionHtml.format(this));
    });
    var cloneHtml = $('.entry-item').remove()[0].outerHTML;
    var dateHeader = $('.date-header').remove()[0].outerHTML;
    newEls = [];
    $.each(hours.entries, function () {
        newEls.push(dateHeader.format(this.date));
        $.each(this.entries, function() {
            newEls.push(cloneHtml.format(this.css_class, this.date, this.mouseover, this.title, this.url));
        });
    });
    $('#entries-container tbody').append($(newEls.join('')));
    headerHeights = $('th').map(function () {
        return $(this).offset().top;
    });
    $(window).on('scroll', function () {
        updateHeaderDate();
    });
    $(document).scrollTop($('th:first').offset().top);
    $('#date-select').on('change', function () {
        window.location.hash = $(this).val();
    });
    $('#date-container').on('mouseenter', function () {
        $('#date-select-container').show();
    }).on('mouseleave', function () {
        $('#date-select-container').hide();
    });
})

