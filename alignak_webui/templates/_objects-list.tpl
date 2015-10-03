%#setdefault('js', ['js/jquery.dataTables.min.js', 'js/dataTables.bootstrap.min.js', 'js/dataTables.responsive.min.js', 'js/buttons.bootstrap.min.js', 'js/buttons.colVis.min.js'])
%#setdefault('css', ['css/jquery.dataTables.min.css', 'css/dataTables.bootstrap.min.css', 'css/responsive.dataTables.min.css', 'css/responsive.bootstrap.min.css', 'css/buttons.bootstrap.min.css', 'css/buttons.dataTables.min.css'])

%# Python imports
%import json

%# Define specific template Js and Css files
%setdefault('js', ['js/jquery.dataTables.js', 'js/dataTables.bootstrap.js', 'js/dataTables.responsive.js', 'js/dataTables.buttons.js', 'js/buttons.bootstrap.js', 'js/buttons.colVis.js'])
%setdefault('css', ['css/jquery.dataTables.css', 'css/dataTables.bootstrap.css', 'css/buttons.dataTables.css', 'css/buttons.bootstrap.css'])

%# Defined by the caller template ...
%setdefault('html_title', 'Objects list')
%setdefault('title', 'Objects list')
%setdefault('subtitle', 'object')

%setdefault('user', app.current_user)

%# Rebase on main application layout
%rebase("application", html_title=html_title, title=title)

%if subtitle:
<h1>{{title}}</h1>
%end
%if subtitle:
<h2>{{subtitle}}</h2>
%end


<hr/>

%if not list:
    <div class="alert alert-info">
        <p class="font-critical">No elements available.</p>
    </div>
%else:
%columns=[]
%for field in fields_list:
    %#if
    %columns.append({"name": field['name'], "data": field['name'], "type": field['type'], "orderable": field['orderable'], "defaultContent": "-/-"})
%end
%data={"data": []}
%for item in list:
%data["data"].append(item)
%end

    <div class="table-responsive">
        <!-- TODO ... data- ... -->
        <table id="tbl_{{object}}" class="table table-striped" data-page-length="25" data-order="[[ 1, &quot;asc&quot; ]]">
            <thead>
                <tr>
                %for field in fields_list:
                <th data-name="{{field['name']}}" data-type="{{field['type']}}">{{field['title']}}</th>
                %end
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>

<script>
$(document).ready(function() {
    var debugJs = true;

    if (debugJs) console.debug("Columns: ", {{! json.dumps(columns)}})
    $('#tbl_{{object}}').DataTable( {
        // Table features
        // Pagination and length change
        "paging": true,
        "lengthChange": true,
        "pageLength": 25,
        "lengthMenu": [ 1, 10, 25, 50, 75, 100 ],
        // Table information
        "info": false,
        // Table ordering
        "ordering": true,

        // Responsive mode
        //responsive: true,

        // Server side processing
        "columns": {{! json.dumps(columns)}},
        "serverSide": true,
        "ajax": {
            //"url": "/{{object}}s_data",
            "url": "/datas/{{object}}",
            "type": "GET",
            "dataSrc": "data",
            "data": function ( d ) {
                // Add an extra field
                d = $.extend({}, d, { "object_type": '{{object}}' });
                // Json stringify to avoid complex array formatting ...
                d.columns = JSON.stringify( d.columns );
                d.search = JSON.stringify( d.search );
                d.order = JSON.stringify( d.order );
                return ( d );
            }
        },

        // Table state saving/restoring
        stateSave: true,
        // Load table parameters
        stateLoadCallback: function (settings) {
            if (debugJs) console.debug("state loading for 'tbl_{{object}}' ...");

            // Get table data from the server ...
            var o;
            $.ajax( {
                "url": "/get_prefs/{{object}}",
                "data": {
                    "user": '{{user.get_username()}}',
                    "type": 'table'
                },
                "async": false,
                "dataType": "json",
                "success": function (json) {
                    if (debugJs) console.debug("state restored for 'tbl_{{object}}' ...", json);
                    o = json;
                }
            } );

            return o;
        },
        // Save table parameters
        stateSaveCallback: function (settings, data) {
            if (debugJs) console.debug("state saving for 'tbl_{{object}}' ...", settings, data);

            // Post table data to the server ...
            $.ajax( {
                "url": "/set_prefs/{{object}}",
                "data": {
                    "user": '{{user.get_username()}}',
                    "type": 'table',
                    // Json stringify to avoid complex array formatting ...
                    "data": JSON.stringify( data )
                },
                "dataType": "json",
                "type": "POST",
                "success": function () {
                    if (debugJs) console.debug("state saved for 'tbl_{{object}}' ...", settings, data);
                }
            } );
        },

        /*
            B - buttons
            l - length changing input control
            f - filtering input
            t - The table!
            i - Table information summary
            p - pagination control
            r - processing display element
        dom: 'Blfrtip',
        */
        dom: 'B<"clearfix">lfrtip',
        // Table columns visibility button
        buttons: [
            'colvis', 'csv'
        ]
    });

    $('#tbl_{{object}}').on( 'xhr.dt', function () {
        var table = $('#tbl_{{object}}').DataTable({ retrieve: true });
        var json = table.ajax.json();
        if (debugJs) console.debug('Datatable event, xhr, url: ' + table.ajax.url());
        if (debugJs) console.debug('Datatable event, xhr, json: ' + table.ajax.json());
        if (debugJs) console.debug('Datatable event, xhr, ' + json.data +' row(s) loaded');
        if (debugJs) console.debug('Datatable event, xhr, ' + json.data.length +' row(s) loaded');
    });

    $('#tbl_{{object}}').on( 'draw.dt', function () {
        if (debugJs) console.debug('Datatable event, draw ...');
    });

    $('#tbl_{{object}}').on( 'error.dt', function ( e, settings ) {
        if (debugJs) console.debug('Datatable event, error ...');
    });

    $('#tbl_{{object}}').on( 'init.dt', function ( e, settings ) {
        if (debugJs) console.debug('Datatable event, init ...');
    });

    $('body').on('click', '#tbl_{{object}} tbody tr', function (e) {
        var table = $('#tbl_{{object}}').DataTable({ retrieve: true });
        if (debugJs) console.debug('Datatable event, click row ...');
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        } else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });
});
</script>
%end
