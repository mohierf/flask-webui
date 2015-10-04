%setdefault("common_bookmarks", prefs_module.get_common_bookmarks() if prefs_module else None)
%setdefault("user_bookmarks", prefs_module.get_user_bookmarks(user) if prefs_module else None)

%#if 'search_engine' in app.request.route.config and app.request.route.config['search_engine']:
%#search_action = app.request.fullpath
%#search_name = app.request.route.name
%#else:
%#search_action = '/all'
%#search_name = ''
%#end

%#search_string = app.get_search_string()

%search_action = '/all'
%search_name = ''
%search_string = 'app.get_search_string()'

<form class="navbar-form hidden-xs" method="get" action="{{ search_action }}">
  <div class="dropdown form-group text-left">
    <button class="btn btn-default dropdown-toggle" type="button" id="filters_menu" data-toggle="dropdown" aria-expanded="true"><i class="fa fa-filter"></i><span class="hidden-sm hidden-xs hidden-md"> Filters</span> <span class="caret"></span></button>
    <ul class="dropdown-menu" role="menu" aria-labelledby="filters_menu">
      <li role="presentation"><a role="menuitem" href="/all?search=&title=All resources">All resources</a></li>
      <li role="presentation"><a role="menuitem" href="/all?search=type:host&title=All hosts">All hosts</a></li>
      <li role="presentation"><a role="menuitem" href="/all?search=type:service&title=All services">All services</a></li>
      <li role="presentation" class="divider"></li>
      <li role="presentation"><a role="menuitem" href="/all?search=isnot:0 isnot:ack isnot:downtime&title=New problems">New problems</a></li>
      <li role="presentation"><a role="menuitem" href="/all?search=is:ack&title=Acknowledged problems">Acknowledged problems</a></li>
      <li role="presentation"><a role="menuitem" href="/all?search=is:downtime&title=Scheduled downtimes">Scheduled downtimes</a></li>
      <li role="presentation" class="divider"></li>
      <li role="presentation"><a role="menuitem" href="?search=bp:>=5">Impact : {{!app.helper.get_business_impact_text(5)}}</a></li>
      <li role="presentation"><a role="menuitem" href="?search=bp:>=4">Impact : {{!app.helper.get_business_impact_text(4)}}</a></li>
      <li role="presentation"><a role="menuitem" href="?search=bp:>=3">Impact : {{!app.helper.get_business_impact_text(3)}}</a></li>
      <li role="presentation"><a role="menuitem" href="?search=bp:>=2">Impact : {{!app.helper.get_business_impact_text(2)}}</a></li>
      <li role="presentation"><a role="menuitem" href="?search=bp:>=1">Impact : {{!app.helper.get_business_impact_text(1)}}</a></li>
      <li role="presentation"><a role="menuitem" href="?search=bp:>=0">Impact : {{!app.helper.get_business_impact_text(0)}}</a></li>
      <li role="presentation" class="divider"></li>
      <li role="presentation"><a role="menuitem" onclick="display_modal('/modal/helpsearch')"><strong><i class="fa fa-question-circle"></i> Search syntax</strong></a></li>
    </ul>
  </div>
  <div class="form-group">
    <label class="sr-only" for="search">Filter</label>
    <div class="input-group">
      <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-search"></i> {{ search_name }}</span>
      <input class="form-control" type="search" id="search" name="search" value="{{ search_string }}">
    </div>
  </div>
  <div class="dropdown form-group text-left">
    <button class="btn btn-default dropdown-toggle" type="button" id="bookmarks_menu" data-toggle="dropdown" aria-expanded="true"><i class="fa fa-bookmark"></i><span class="hidden-sm hidden-xs hidden-md"> Bookmarks</span> <span class="caret"></span></button>
    <ul class="dropdown-menu dropdown-menu-right" role="menu" aria-labelledby="bookmarks_menu">
      <script type="text/javascript">
         %if user_bookmarks:
         %for b in user_bookmarks:
            declare_bookmark("{{!b['name']}}","{{!b['uri']}}");
         %end
         %end
         %if common_bookmarks:
         %for b in common_bookmarks:
            declare_bookmarksro("{{!b['name']}}","{{!b['uri']}}");
         %end
         %end
      </script>
    </ul>
  </div>
</form>