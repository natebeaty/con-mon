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
        calendars.clndr1 = $('.cal1').clndr({
          events: eventsArray,
          clickEvents: {
            click: function(target) {
              console.log(target);
            }
          },
          multiDayEvents: {
            startDate: 'start_date',
            endDate: 'end_date'
          },
          showAdjacentMonths: true,
          adjacentDaysChangeMonth: false
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
