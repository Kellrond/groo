# All new widgets must be added here for the page builder to find
from www.views.developer.widgets.configuration  import GlogbalConfigWidget
from www.views.developer.widgets.database       import DatabaseControlWidget, DatabaseStatsWidget, SqlConsoleWidget, SqlResultsWidget 
from www.views.developer.widgets.documentation  import DocsAdminWidget, DocsRoutesWidget, DocsWidget, DocsImportdependencyWidget
from www.views.developer.widgets.logging        import ActivityLogWidget, AnalyticsResultSummaryWidget, ApacheAccessWidget, ApacheErrorWidget, ErrorAlertWidget, LoggingSearchWidget