// con-mon!
// nate@clixel.com

// @codekit-prepend "../bower_components/jquery/dist/jquery.js"
// @codekit-prepend "../bower_components/underscore/underscore.js"
// @codekit-prepend "../bower_components/moment/moment.js"
// @codekit-prepend "../bower_components/tooltipster/dist/js/tooltipster.bundle.js"
// @codekit-prepend "../bower_components/clndr/src/clndr.js"
// @codekit-prepend "../bower_components/jquery.quicksearch/dist/jquery.quicksearch.js"
// @codekit-prepend "bootstrap-datepicker.js"

var CON_MON = (function() {
  var medium_width = false,
    small_width = false,
    calendars = {}
    eventArray = [];

  function _init() {
    _resize();

    // init submission form handlers
    $('.show-submit-condate').click(function(e) {
      e.preventDefault();
      $('.submit-condate').toggleClass('hidden');
    });
    // "other convention" fields hide/show
    $('#convention').on('change', function() {
      $('.other-fields').toggleClass('hidden', $(this).val() != 'other');
    });

    // Homepage
    if ($('body#home').length) {
      // pull in condate data and build year view
      $.getJSON( '/condates.json', function( data ) {
        eventsArray = data.condates;
        _initClndr();
      });

      // hide any unused tags
      $('.filtering .tag').each(function() {
        $(this).toggleClass('hidden', $('.condate.tagged-' + $(this).text()).length===0);
      });
      // totally hide filters if there's only one
      $('.filtering').toggleClass('hidden', $('p.tags .tag:not(.hidden)').length===1);

      // init condate filters
      _filterCondates();
    }

    // Bulk condates page
    if ($('body#condates').length) {
      // Kill form submit that we don't really need (just quicksearch)
      $('.quicksearch').on('submit', function(e) {
        e.preventDefault();
      }).find('input[name="term"]').focus();
      // Add "no results" li for quicksearch
      $('<article class="no-results hidden">None found.</article>').appendTo('.conventions');
      $(document).on('keydown',function(e) {
        // Escape clears out search
        if (e.keyCode === 27) {
          $('.quicksearch input[name="term"]').val('');
        }
      });
      _initQuickSearch();

      // Bulk forms
      $('a.add-new-condate').on('click', function(e) {
        e.preventDefault();
        $form = $(this).next('form').toggleClass('hidden');
      });
      $('.convention form').on('submit', function(e) {
        e.preventDefault();
        $form = $(this);
        if ($form.find('input[name=diebots_5000]').val() == '') {
          $.post('/submit_condate', $form.serialize())
            .done(function(data) {
              if (data.success) {
                $form.addClass('submitted-ok').find('.status').removeClass('error').addClass('success').text(data.message);
              } else {
                $form.find('.status').addClass('error').text(data.message);
              }
            })
            .fail(function() {
              $form.find('.status').addClass('error').text('There was an error. Please try again.');
            });
        }
      });

    }

    // change datepickers to native if on mobile and input type=date is supported
    // if (Modernizr.inputtypes.date && Modernizr.touch) {
    //   $('.dp').attr('type', 'date').prev('label').addClass('showme');
    // } else {
      $('.submit-condate').each(function() {
        var $this = $(this);
        _startEndDatepickers($this.find('input[name=start_date]'), $this.find('input[name=end_date]'), 1);
        _startEndDatepickers($this.find('input[name=registration_opens]'), $this.find('input[name=registration_closes]'));
      });
    // }

  }

  function _startEndDatepickers($el1, $el2, populateEnd) {
    var nowTemp = new Date();
    var now = new Date(nowTemp.getFullYear(), nowTemp.getMonth(), nowTemp.getDate(), 0, 0, 0, 0);
    var startDate = $el1.datepicker({
      format: 'yyyy-mm-dd',
      onRender: function(date) {
        return date.valueOf() < now.valueOf() ? 'disabled' : '';
      }
    }).on('changeDate', function(ev) {
      if (ev.date.valueOf() > endDate.date.valueOf()) {
        var newDate = new Date(ev.date)
        newDate.setDate(newDate.getDate());
        if (typeof populateEnd !== 'undefined') {
          endDate.setValue(newDate);
        }
      }
      startDate.hide();
      $el2[0].focus();
    }).data('datepicker');

    var endDate = $el2.datepicker({
      format: 'yyyy-mm-dd',
      onRender: function(date) {
        return date.valueOf() < startDate.date.valueOf() ? 'disabled' : '';
      }
    }).on('changeDate', function(ev) {
      endDate.hide();
    }).data('datepicker');
  }

  // Quick search on top of /artists/ page
  function _initQuickSearch() {
    $('.quicksearch input[name="term"]').quicksearch('.conventions article.convention', {
      onAfter: function () {
        $('.conventions').toggleClass('searching', $('.quicksearch input[name="term"]').val()!=='');
      },
      selector: 'h2, p.city',
      noResults: '.no-results'
    });
  }

  function _initClndr() {
    // build year view of calendars
    for (var i = 1; i < 13; i++) {
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
    // filter condates by tag
    $('.tags').on('click', 'a', function(e) {
      e.preventDefault();
      // ensure one tag is always selected
      if ($('.tags a.on').length==1 && $(this).hasClass('on')) return;
      $(this).toggleClass('on');
      _filterCondates();
    });

    // highlight event dates on hover
    $('.event').each(function() {
      var $tip = $(this).find('.event-detail');
      var $this = $(this);
      $.each( $tip.attr('class').split(/\s+/), function(index, item){
        if (item != 'event-detail') {
           $this.addClass(item);
        }
      });
      // mark as multiple events for css styling
      if ($this.find('.event-detail h3').length>1) $this.addClass('multiple-events');
      $this.on('mouseenter', function() {
        var id = $(this).find('h3:first').data('condate-id');
        $('.days li').removeClass('current');
        $dates = $('.event-detail h3[data-condate-id="'+id+'"]');
        $dates.each(function() {
          $(this).parents('li:first').addClass('current');
        });
      }).on('mouseleave', function() {
        $('.days li').removeClass('current');
      });
      $this.tooltipster({
        content: $tip.text(),
        delay: 0,
        delayTouch: [0, 2500]
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
    $('.condate').addClass('inactive').removeClass('accent');
    $('.tag.on').each(function() {
      $('.condate.tagged-' + $(this).text()).removeClass('inactive');
    });
    $('.condate:visible:odd').addClass('accent');
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
// handle mothership zigs and zags
$(window).resize(function(){
  CON_MON.resize();
});
