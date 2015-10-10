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

/* Default is a string defined in WebUI configuration */
var search_filter = app_search_string;

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
function do_refresh_livestate(search){
   if (! $('#livestate-list').length) {
      // No refresh needed ...
      return false
   }

   if (refresh_logs) console.debug("Refreshing system live state, filter: ", search);

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

      // Hosts pie chart
      if ($("#chart-hosts").length !== 0) {
         synthesis = html['livesynthesis']['hosts_synthesis'];

         var data = [];
         $.each(pie_hosts_graph_states, function( index, value ) {
            // Update table rows
            row = pie_hosts_graph_parameters[value];
            row['value'] = synthesis['nb_'+value]
            data.push(row)

            if (states_queue["nb_"+value].length > hosts_states_queue_length) {
               states_queue["nb_"+value].shift();
            }
            states_queue["nb_"+value].push(synthesis['nb_'+value]);
         });

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-hosts canvas").get(0).getContext("2d");
         var myPieChart = new Chart(ctx).Doughnut(data, pie_hosts_graph_options);
         $("#chart-hosts span.subtitle").html(synthesis['nb_elts'] + " hosts");
         if (pie_hosts_graph_options) {
            if ($("#chart-hosts span.legend").length) {
               if (! $("#pie_hosts_graph_options-legend").length) {
                  $("#chart-hosts span.legend").append(myPieChart.generateLegend());
               }
            }
         }
      }

      // Hosts line chart
      if ($("#chart-hosts-serie").length !== 0) {
         synthesis = html['livesynthesis']['hosts_synthesis'];

         var data = [];
         data['labels'] = line_hosts_graph_data['labels'];
         data['datasets'] = [];
         $.each(line_hosts_graph_states, function( index, value ) {
            // Update table rows
            row = line_hosts_graph_data['datasets'][value];
            row['data'] = states_queue["nb_"+value];
            data['datasets'].push(row);
         });

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-hosts-serie canvas").get(0).getContext("2d");
         var myLineChart = new Chart(ctx).Line(data, line_hosts_graph_options);
         $("#chart-hosts-serie span.subtitle").html(synthesis['nb_elts'] + " hosts (progression)");
         if (line_hosts_graph_options) {
            if ($("#chart-hosts-serie span.legend").length) {
               if (! $("#line_hosts_graph_options-legend").length) {
                  $("#chart-hosts-serie span.legend").append(myLineChart.generateLegend());
               }
            }
         }
      }

      // Services pie chart
      if ($("#chart-services").length !== 0) {
         synthesis = html['livesynthesis']['services_synthesis'];

         var data = [];
         $.each(pie_services_graph_states, function( index, value ) {
            // Update table rows
            row = pie_services_graph_parameters[value];
            row['value'] = synthesis['nb_'+value]
            data.push(row)

            if (states_queue["nb_"+value].length > services_states_queue_length) {
               states_queue["nb_"+value].shift();
            }
            states_queue["nb_"+value].push(synthesis['nb_'+value]);
         });

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-services canvas").get(0).getContext("2d");
         var myPieChart = new Chart(ctx).Doughnut(data, pie_services_graph_options);
         $("#chart-services span.subtitle").html(synthesis['nb_elts'] + " services");
         if (pie_services_graph_options) {
            if ($("#chart-services span.legend").length) {
               if (! $("#pie_services_graph_options-legend").length) {
                  $("#chart-services span.legend").append(myPieChart.generateLegend());
               }
            }
         }
      }

      // Services line chart
      if ($("#chart-services-serie").length !== 0) {
         synthesis = html['livesynthesis']['services_synthesis'];

         var data = [];
         data['labels'] = line_services_graph_data['labels'];
         data['datasets'] = [];
         $.each(line_services_graph_states, function( index, value ) {
            console.log(index, value)
            // Update table rows
            row = line_services_graph_data['datasets'][value];
            row['data'] = states_queue["nb_"+value];
            data['datasets'].push(row);
         });

         // Get the context of the canvas element we want to select
         var ctx = $("#chart-services-serie canvas").get(0).getContext("2d");
         var myLineChart = new Chart(ctx).Line(data, line_services_graph_options);
         $("#chart-services-serie span.subtitle").html(synthesis['nb_elts'] + " services (progression)");
         if (line_services_graph_options) {
            if ($("#chart-services-serie span.legend").length) {
               if (! $("#line_services_graph_options-legend").length) {
                  $("#chart-services-serie span.legend").append(myLineChart.generateLegend());
               }
            }
         }
      }
   });

   var bi;
   for (bi = 5; bi >= 0; --bi) {
      // Request to update each possible Business impact ...
      $.ajax({
         url: "/refresh_livestate",
         data: {
            "bi": bi,
            "filter": search
         },
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

            // Update table rows ...
            $.each(html['livestate']['rows'], function( index, value ) {
               if (refresh_logs) console.debug("Row:", index);
               // Update table rows
               $('#livestate-bi-'+bi+' table tbody').append(value);
            });
         } else {
            $('#livestate-bi-'+bi).hide(1000, function() {
               // Replace existing panel ...
               $('#livestate-bi-'+bi).replaceWith(html['livestate']['panel_bi']);

               // Update table rows ...
               $.each(html['livestate']['rows'], function( index, value ) {
                  if (refresh_logs) console.debug("Row:", index);
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
   if (refresh_logs) console.debug("Refreshing page, timeout: ", refresh_timeout);

   // We will first get the application parameters (search string, ...)

   // Request search string ...
   $.ajax({
      url: "/app_settings",
      method: "get",
      dataType: "json"
   })
   .done(function(html, textStatus, jqXHR) {
      search_filter = html.search_string;

      // Refresh current page ...

      // Refresh page header ...
      do_refresh_header();

      // Refresh livestate ...
      do_refresh_livestate(search_filter);
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

/*
 * Global Ajax event handlers - all Ajax requests are concerned ...
 */

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

/*
 * Document loaded
 */
$( document ).ready(function() {
   // Start refresh periodical check ...
   setInterval("check_refresh();", 1000);

   // Force first refresh ...
   do_refresh();
});
