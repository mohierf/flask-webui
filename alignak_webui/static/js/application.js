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

/*
 * For IE missing window.console ...
*/
(function () {
    var f = function () {};
    if (!window.console) {
        window.console = {
            log:f, info:f, warn:f, debug:f, error:f
        };
    }
}());

$(document).ready(function(){
   // When modal box is hidden ...
   $('#modal').on('hidden.bs.modal', function () {
      // Show sidebar menu ...
      $('.sidebar').show();
      // Show actions bar ...
      $('.actionbar').show();

      // Clean modal box content ...
      $(this).removeData('bs.modal');
   });

   // When modal box is displayed ...
   $('#modal').on('shown.bs.modal', function () {
      // Hide sidebar menu ...
      $('.sidebar').hide();
      // Hide actions bar ...
      $('.actionbar').hide();
   });

   // Sidebar menu
   $('#sidebar-menu').metisMenu();

   // Actions bar menu
   $('#actions-menu').metisMenu();
});

// Play alerting sound ...
function playAlertSound() {
   var audio = document.getElementById('alert-sound');
   var canPlay = audio && !!audio.canPlayType && audio.canPlayType('audio/wav') != "";
   if (canPlay) {
      audio.play();
      sessionStorage.setItem("sound_play", "1");
      $('#sound_alerting i.fa-ban').addClass('hidden');
   }
}
