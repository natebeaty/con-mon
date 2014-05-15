// concalendar
// nate@clixel.com

$.concalendar = (function() {
    var medium_width = false,
        small_width = false,
        calendars = {}
        eventArray = [];
        $.getJSON( "/condates.json", function( data ) {
            eventsArray = data;
            _initClndr();
        });

    function _init() {
        _resize();
    }

    function _initClndr() {
        for (var i = 0; i < 13; i++) {
            calendars.clndr1 = $('.cal'+i).clndr({
                template: $('#template-calendar').html(),
                startWithMonth: moment().add('month', i-1),
                events: eventsArray,
                clickEvents: {
                    click: function(target) {
                        if (target.events.length > 0) {
                            // console.log($(this).find('.event-details'));
                        }
                    }
                },
                multiDayEvents: {
                startDate: 'start_date',
                endDate: 'end_date'
                },
                showAdjacentMonths: false,
                adjacentDaysChangeMonth: false
            });
        }
        $('.event').each(function() {
            var tip = $(this).find('.event-detail').html();
            $(this).tooltipster({
                content: tip,
                contentAsHTML: true,
                animation: 'fade',
                delay: 0
            });
        });
    }

    function _resize() {
        var screen_width = document.documentElement.clientWidth;
        medium_width = screen_width <= 768;
        small_width = screen_width <= 480;
    }

    // public methods
    return {
        resize: function() {
            _resize();
        },
        init: function() {
            _init();
        }
    };
})();

// fire up the mothership
$(document).ready(function(){
    $.concalendar.init();
});
$(window).resize(function(){
    $.concalendar.resize();
});
