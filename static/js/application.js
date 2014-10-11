// con-mon!
// nate@clixel.com

// @codekit-prepend "../bower_components/jquery/dist/jquery.js"
// @codekit-prepend "../bower_components/underscore/underscore.js"
// @codekit-prepend "../bower_components/moment/moment.js"
// @codekit-prepend "../bower_components/tooltipster/js/jquery.tooltipster.js"
// @codekit-prepend "../bower_components/clndr/src/clndr.js"
// @codekit-prepend "bootstrap-datepicker.js"

CON_MON = (function() {
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
        $.getJSON( '/condates.json', function( data ) {
            eventsArray = data;
            _initClndr();
        });
        $('.dp').datepicker({
            format: 'yyyy-mm-dd'
        }).on('changeDate', function () {
            $(this).datepicker('hide');
        });
        _filterCondates();
        $('.show-submit-condate').click(function(e) {
            e.preventDefault();
            $('.submit-condate').toggleClass('hidden');
            $('.submit-note').toggleClass('hidden', !$('.submit-condate').hasClass('hidden'));
        });
        $('.show-submit-note').click(function(e) {
            e.preventDefault();
            $('.submit-note').toggleClass('hidden');
            $('.submit-condate').toggleClass('hidden', !$('.submit-note').hasClass('hidden'));
        });
        $('#convention').on('change', function() {
            $('.other-fields').toggleClass('hidden', $(this).val() != 'other');
        });
    }

    function _initClndr() {
        for (var i = 0; i < 13; i++) {
            calendars.clndr1 = $('.cal'+i).clndr({
                template: $('#template-calendar').html(),
                startWithMonth: moment().add(i-1, 'month'),
                events: eventsArray,
                clickEvents: {
                    click: function(target) {
                        if (target.events.length == 1) {
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
        $('.tags').on('click', 'a', function(e) {
            e.preventDefault();
            // ensure one tag is always selected
            if ($('.tags a.on').length==1 && $(this).hasClass('on')) return;
            $(this).toggleClass('on');
            _filterCondates();
        });
        $('.event').each(function() {
            var $tip = $(this).find('.event-detail');
            $(this).on('mouseenter', function() {
                var id = $(this).find('h3:first').data('condate-id');
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
        // $('.upcoming tr').on('mouseenter', function() {
        //     if ($(this).hasClass('inactive')) return;
        //     var id = $(this).data('condate-id');
        //     $('.cal,.days li').addClass('inactive');
        //     $dates = $('.event-detail h3[data-condate-id="'+id+'"]');
        //     $dates.each(function() {
        //         $(this).parents('li:first').removeClass('inactive'); //.tooltipster('show');
        //         $(this).parents('.cal:first').removeClass('inactive');
        //     });
        // }).on('mouseleave', function() {
        //     $('.days li,.cal').removeClass('inactive');
        //     // $('.tooltipstered').tooltipster('hide');
        // });
        $('body').addClass('loaded');
    }
    function _filterCondates() {
        $('.condate').addClass('inactive');
        $('.tag.on').each(function() {
            $('.condate.tag-' + $(this).text()).removeClass('inactive');
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
    CON_MON.init();
});
$(window).resize(function(){
    CON_MON.resize();
});
