/*
# Copyright (c) 2015:
#   Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of (WebUI).
*
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
*/

var refresh_logs=true;

/* Default is an empty value for the search filter ... */
var search_filter = "";

/* Default is to set the page to reload each period defined in WebUI configuration */
var refresh_timeout = app_refresh_period;
var nb_refresh_retry = 0;

/*
 * This function is called on each refresh of the current page.
 * ----------------------------------------------------------------------------
 *  This function refreshes the page header elements:
 * - #overall-hosts-states
 * - #overall-services-states
 * => These elements are the real "dynamic" elements in the page header ...
 * ---------------------------------------------------------------------------
 */
function do_refresh_header(){
   if ($('#hosts-states-popover-content').length == 0 &&
         $('#services-states-popover-content').length == 0) {
      // No refresh needed ...
      return false
   }

   if (refresh_logs) console.debug("Refreshing page header");

   $.ajax({
      url: "/refresh_header",
      method: "get",
      dataType: "json"
   })
   .done(function(html, textStatus, jqXHR) {
      /*
       * Update page header : live synthesis
       */
      if (! html['livesynthesis']) {
         return
      }
      // Refresh header bar hosts/services state ...
      if (
            $('#hosts-states-popover-content').length > 0 &&
            html['livesynthesis']['hosts_states_popover'] &&
            $('#services-states-popover-content').length > 0 &&
            html['livesynthesis']['services_states_popover']
         ) {
         // Update popovers content
         $('#hosts-states-popover-content').html(html['livesynthesis']['hosts_states_popover']);
         $('#services-states-popover-content').html(html['livesynthesis']['services_states_popover']);

         // Compute problems
         var nb_problems=0;
         $('#hosts-states-popover-content tr').each(function () {
            nb_problems += parseInt($(this).data("problems"));
         });
         $('#services-states-popover-content tr').each(function () {
            nb_problems += parseInt($(this).data("problems"));
         });
         if (refresh_logs) console.debug("Hosts/Services problems", nb_problems);

         var popoverTemplate = [
            '<div class="popover img-popover">',
            '<div class="arrow"></div>',
            '<div class="popover-inner">',
            '<h3 class="popover-title"></h3>',
            '<div class="popover-content"></div>',
            '</div>',
            '</div>'
         ].join('');

         // Update navbar icon
         $('#overall-hosts-states').html(html['livesynthesis']['hosts_state']);
         // Activate the header hosts state popover ...
         $('#overall-hosts-states a').popover({
            trigger: 'focus hover',
            placement: 'bottom',
            animation: true,
            html: true,
            template: popoverTemplate,
            container: 'body',
            content: function() {
               return $('#hosts-states-popover-content').html();
            }
         });

         // Update navbar icon
         $('#overall-services-states').html(html['livesynthesis']['services_state']);
         // Activate the header services state popover ...
         $('#overall-services-states a').popover({
            trigger: 'focus hover',
            placement: 'bottom',
            animation: true,
            html: true,
            template: popoverTemplate,
            container: 'body',
            content: function() {
               return $('#services-states-popover-content').html();
            }
         });

         var old_problems = Number(sessionStorage.getItem("how_many_problems_actually"));
         // Sound alerting
         if (sessionStorage.getItem("sound_play") == '1') {
            if (! sessionStorage.getItem("how_many_problems_actually")) {
               // Default is current value ...
               sessionStorage.setItem("how_many_problems_actually", nb_problems);
            }
            if (refresh_logs) console.debug("Hosts/Services - stored problems number:", old_problems);
            if (old_problems < nb_problems) {
               if (refresh_logs) console.debug("Dashboard - play sound!");
               playAlertSound();
            }
         }
         sessionStorage.setItem("how_many_problems_actually", nb_problems);
      }
   });
}

/*
 * This function is called on each refresh of the current page.
 * ----------------------------------------------------------------------------
 *  This function refreshes the system live state table:
 * - #livestate
 * => These elements are the real "dynamic" elements in the page content ...
 * ---------------------------------------------------------------------------
 */
var queue = {
   "nb_up": [],
   "nb_unreachable": [],
   "nb_down": [],

   "nb_ok": [],
   "nb_warning": [],
   "nb_critical": []
}
function do_refresh_livestate(){
   if (! $('#livestate-list').length) {
      // No refresh needed ...
      return false
   }

   if (refresh_logs) console.debug("Refreshing system live state");

   // Request livestate synthesis ...
   $.ajax({
      url: "/livesynthesis",
      method: "get",
      dataType: "json"
   })
   .done(function(html, textStatus, jqXHR) {
      if (refresh_logs) console.debug("Livesynthesis:", html);
      /*
       * Update page header : live synthesis
       */
      if (! html['livesynthesis']) {
         return
      }

      if ($("#chart-hosts").length !== 0) {
         synthesis = html['livesynthesis']['hosts_synthesis'];
         // Hosts pie chart
         var data = [
            {
               value: synthesis['nb_up'],
               color:"#5bb75b",
               highlight: "#5AD3D1",
               label: "Up"
            },
            {
               value: synthesis['nb_unreachable'],
               color: "#faa732",
               highlight: "#5AD3D1",
               label: "Unreachable"
            },
            {
               value: synthesis['nb_down'],
               color: "#da4f49",
               highlight: "#5AD3D1",
               label: "Down"
            }
          ]
         if (queue["nb_up"].length > 10) {
            queue["nb_up"].shift();
         }
         queue["nb_up"].push(synthesis['nb_up']);

         if (queue["nb_unreachable"].length > 10) {
            queue["nb_unreachable"].shift();
         }
         queue["nb_unreachable"].push(synthesis['nb_unreachable']);

         if (queue["nb_down"].length > 10) {
            queue["nb_down"].shift();
         }
         queue["nb_down"].push(synthesis['nb_down']);

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-hosts canvas").get(0).getContext("2d");
         var myPieChart = new Chart(ctx).Pie(data);
         $("#chart-hosts span").html(synthesis['nb_elts'] + " hosts");
      }
      if ($("#chart-hosts-serie").length !== 0) {
         synthesis = html['livesynthesis']['hosts_synthesis'];
         // Line chart
         var data = {
            labels: ["-9", "-8", "-7", "-6", "-5", "-4", "-3", "-2", "-1", "0"],
            datasets: [
               {
                  label: "Hosts up",
                  fillColor: "rgba(91,183,91,0.2)",
                  strokeColor: "rgba(91,183,91,1)",
                  pointColor: "rgba(91,183,91,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(220,220,220,1)",
                  data: queue["nb_up"]
               },
               {
                  label: "Hosts unreachable",
                  fillColor: "rgba(250,167,50,0.2)",
                  strokeColor: "rgba(250,167,50,1)",
                  pointColor: "rgba(250,167,50,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(151,187,205,1)",
                  data: queue["nb_unreachable"]
               },
               {
                  label: "Hosts down",
                  fillColor: "rgba(218,79,73,0.2)",
                  strokeColor: "rgba(218,79,73,1)",
                  pointColor: "rgba(218,79,73,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(220,220,220,1)",
                  data: queue["nb_down"]
               }
           ]
         };

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-hosts-serie canvas").get(0).getContext("2d");
         // var ctx = document.getElementById("myChart1").getContext("2d");
         var myLineChart = new Chart(ctx).Line(data);
         $("#chart-hosts-serie span").html(synthesis['nb_elts'] + " hosts (progression)");
      }
      if ($("#chart-services").length !== 0) {
         synthesis = html['livesynthesis']['services_synthesis'];
         // Pie chart
         var data = [
            {
               value: synthesis['nb_ok'],
               color:"#5bb75b",
               highlight: "#5AD3D1",
               label: "Ok"
            },
            {
               value: synthesis['nb_warning'],
               color: "#faa732",
               highlight: "#5AD3D1",
               label: "Warning"
            },
            {
               value: synthesis['nb_critical'],
               color: "#da4f49",
               highlight: "#5AD3D1",
               label: "Critical"
            }
          ]
         if (queue["nb_ok"].length > 10) {
            queue["nb_ok"].shift();
         }
         queue["nb_ok"].push(synthesis['nb_ok']);

         if (queue["nb_warning"].length > 10) {
            queue["nb_warning"].shift();
         }
         queue["nb_warning"].push(synthesis['nb_warning']);

         if (queue["nb_critical"].length > 10) {
            queue["nb_critical"].shift();
         }
         queue["nb_critical"].push(synthesis['nb_critical']);

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-services canvas").get(0).getContext("2d");
         var myPieChart = new Chart(ctx).Pie(data);
         $("#chart-services span").html(synthesis['nb_elts'] + " services");
      }
      if ($("#chart-services-serie").length !== 0) {
         synthesis = html['livesynthesis']['services_synthesis'];
         // Line chart
         var data = {
            labels: ["-9", "-8", "-7", "-6", "-5", "-4", "-3", "-2", "-1", "0"],
            datasets: [
               {
                  label: "Services ok",
                  fillColor: "rgba(91,183,91,0.2)",
                  strokeColor: "rgba(91,183,91,1)",
                  pointColor: "rgba(91,183,91,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(220,220,220,1)",
                  data: queue["nb_ok"]
               },
               {
                  label: "Services warning",
                  fillColor: "rgba(250,167,50,0.2)",
                  strokeColor: "rgba(250,167,50,1)",
                  pointColor: "rgba(250,167,50,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(151,187,205,1)",
                  data: queue["nb_warning"]
               },
               {
                  label: "Services critical",
                  fillColor: "rgba(218,79,73,0.2)",
                  strokeColor: "rgba(218,79,73,1)",
                  pointColor: "rgba(218,79,73,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(220,220,220,1)",
                  data: queue["nb_critical"]
               }
           ]
         };

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-services-serie canvas").get(0).getContext("2d");
         // var ctx = document.getElementById("myChart1").getContext("2d");
         var myLineChart = new Chart(ctx).Line(data, {
            bezierCurve: true,
            legendTemplate : [
               "<ul class=\"<%=name.toLowerCase()%>-legend\">",
                  "<% for (var i=0; i<datasets.length; i++){%>",
                     "<li>",
                        "<span style=\"background-color:<%=datasets[i].strokeColor%>\"></span>",
                        "<%=datasets[i].label%>",
                        "<%if(datasets[i].label){%>",
                           "<%=datasets[i].label%>",
                        "<%}%>",
                     "</li>",
                  "<%}%>",
               "</ul>"
            ].join('')
         });
         $("#chart-services-serie span").html(synthesis['nb_elts'] + " services (progression)");
      }
   });

   var bi;
   for (bi = 5; bi >= 0; --bi) {
      // Request to update each possible Business impact ...
      $.ajax({
         url: "/refresh_livestate",
         data: { 'bi': bi },
         method: "get",
         dataType: "json"
      })
      .done(function(html, textStatus, jqXHR) {
         if (refresh_logs) console.debug("Livestate:", html);
         /*
          * Update page header : live synthesis
          */
         if (! html['livestate']) {
            return
         }

         var bi = parseInt(html['livestate']['bi']);
         var rows = html['livestate']['rows'];
         if (! rows.length) {
            if (refresh_logs) console.debug("No data for BI:", bi);
            return
         }
         if (refresh_logs) console.debug("Received Livestate for BI:", bi);

         if (! $('#livestate-bi-'+bi).length) {
            $('#livestate-list').append(html['livestate']['panel_bi']);
            $.each(html['livestate']['rows'], function( index, value ) {
               // Update table rows
               $('#livestate-bi-'+bi+' table tbody').append(value);
            });
         } else {
            $('#livestate-bi-'+bi).hide(1000, function() {
               // Replace existing panel ...
               $('#livestate-bi-'+bi).replaceWith(html['livestate']['panel_bi']);
               $.each(html['livestate']['rows'], function( index, value ) {
                  // Update table rows
                  $('#livestate-bi-'+bi+' table tbody').append(value);
               });
               $('#livestate-bi-'+bi).show(500);
            });
         }
      });
   }
}


/* We will try to see if the UI is not in restating mode, and so
   don't have enough data to refresh the page as it should ... */
function do_refresh() {
   if (refresh_logs) console.debug("Refreshing search string, timeout: ", refresh_timeout);

   // We will first check if the backend is available or not. It's useless to refresh
   // if the backend is reloading, because it will prompt for login, but waiting a little
   // will make the data available.

   // Request search string ...
   $.ajax({
      url: "/search_string",
      method: "get",
      dataType: "json"
   })
   .done(function(html, textStatus, jqXHR) {
      if (refresh_logs) console.log(html);

      // Refresh current page ...

      // Refresh page header ...
      do_refresh_header();

      // Refresh livestate ...
      do_refresh_livestate();
   });
}


/* We will try to see if the UI is not in restating mode, and so
   don't have enough data to refresh the page as it should ... */
function check_UI_backend(){
   reset_refresh();

   $.ajax({
      url: '/ping'
   })
   .done(function( data, textStatus, jqXHR ) {
      if (refresh_logs) console.log('Pong: ', data);
      if (sessionStorage.getItem("refresh_active") == '1') {
         nb_refresh_retry = 0;

         // Go Refresh
         do_refresh();
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      if (refresh_logs) console.error('UI backend is not available, retrying later ...');

      // Postpone refresh ... we will come back later.
      postpone_refresh();
   });
}


/* Each second, we check for timeout and restart page */
function check_refresh() {
   if (sessionStorage.getItem("refresh_active") == '1') {
      if (refresh_logs) console.debug("check_refresh: " + refresh_timeout + " seconds");
      if (refresh_timeout < 0) {
         check_UI_backend();
      }
      refresh_timeout -= 1;
   } else {
      nb_refresh_retry = 0;
      refresh_timeout = app_refresh_period;
   }
}

/* Postpone refresh */
function postpone_refresh() {
   // If we are not in our first try, warn the user
   if (nb_refresh_retry > 0) {
      alertify.log("The Web UI backend is not available", "info", 5000);
   }
   nb_refresh_retry += 1;

   // Start a new loop before retrying ...
   reset_refresh();
}

/* Restart the refresh period */
function reset_refresh() {
   refresh_timeout = app_refresh_period;

   if (nb_refresh_retry > 3) {
      // Reset refresh period and refresh retry
      refresh_timeout = 1.3 * app_refresh_period;
   } else if (nb_refresh_retry > 6) {
      // Reset refresh period and refresh retry
      refresh_timeout = 1.6 * app_refresh_period;
   } else if (nb_refresh_retry > 6) {
      nb_refresh_retry = 0;
      refresh_timeout = app_refresh_period;
   }
   if (refresh_logs) console.debug("Refresh period restarted: " + nb_refresh_retry + " attempts, " + refresh_timeout + " seconds");
}


// Global Ajax event handler - First Ajax request sent ...
$( document ).ajaxStart(function() {
   if (sessionStorage.getItem("refresh_active") == '1') {
      // Refresh starting indicator ...
      $('#app_refreshing').addClass('fa-spin');
   }
});
// Global Ajax event handler - Last Ajax request completed ...
$( document ).ajaxStop(function() {
   if (sessionStorage.getItem("refresh_active") == '1') {
      // Refresh is finished
      $('#app_refreshing').removeClass('fa-spin');
   }
});
// Global Ajax event handler - Ajax error ...
$( document ).ajaxError(function( event, jqxhr, settings, thrownError ) {
   console.error("Ajax error.", thrownError, settings.url);
   if (refresh_logs) console.error("Details:");
   if (refresh_logs) console.error(jqxhr);
   if (refresh_logs) console.error(settings);
});

$( document ).ready(function() {
   // Start refresh periodical check ...
   setInterval("check_refresh();", 1000);

   // Force first refresh ...
   do_refresh();

   // Search filter changed in the header input form ...
   $('#nav-bar-form').on('submit', function(event) {
      var $form = $(this);

      // Block automatic submission ...
      event.preventDefault();

      $.ajax({
         type: $form.attr('method'),
         url: $form.attr('action'),
         data: $form.serialize()
      })
      .done(function(html, textStatus, jqXHR) {
         if (refresh_logs) console.debug("Refreshing search string: ", html);

      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         if (refresh_logs) console.error(jqXHR, errorThrown);
         if (refresh_logs) console.error(jqXHR. responseText);
      })
      .always(function() {
      });
   });
});
