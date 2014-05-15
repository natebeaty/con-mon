// concalendar
// nate@clixel.com

$.concalendar = (function() {
    var medium_width = false,
        small_width = false,
        calendars = {}
        eventArray = [];

    function _init() {
        _resize();
        $('.tooltip').tooltipster({
            delay: 0,
            animation: 'slide'
        });
        $.getJSON( "/condates.json", function( data ) {
            eventsArray = data;
            _initClndr();
        });
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
            var $tip = $(this).find('.event-detail');
            $(this).on('mouseenter', function() {
                var id = $(this).find('h3:first').data('condate-id');
                console.log(id);
                $('.days li').removeClass('current');
                $dates = $('.event-detail h3[data-condate-id="'+id+'"]');
                $dates.each(function() {
                    $(this).parents('li:first').addClass('current');
                });
            }).on('mouseleave', function() {
                $('.days li').removeClass('current');
            });
            $(this).tooltipster({
                content: $tip.html(),
                delay: 0,
                contentAsHTML: true,
                animation: 'slide',
                delay: 0
            });
        });
        $('.upcoming li a').on('mouseenter', function() {
            var id = $(this).parents('li:first').data('condate-id');
            $('.cal,.days li').addClass('inactive');
            $dates = $('.event-detail h3[data-condate-id="'+id+'"]');
            $dates.each(function() {
                $(this).parents('li:first').removeClass('inactive'); //.tooltipster('show');
                $(this).parents('.cal:first').removeClass('inactive');
            });
        }).on('mouseleave', function() {
            $('.days li,.cal').removeClass('inactive');
            // $('.tooltipstered').tooltipster('hide');
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
