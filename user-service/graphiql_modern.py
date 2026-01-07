
# Universal GraphiQL (v1.4.2) HTML Template
# This version is extremely stable and has the "Request Headers" tab built-in.
MODERN_GRAPHIQL_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        height: 100%;
        margin: 0;
        width: 100%;
        overflow: hidden;
      }
      #graphiql {
        height: 100vh;
      }
    </style>
    <script crossorigin src="https://unpkg.com/react@16/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@16/umd/react-dom.production.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/graphiql@1.4.2/graphiql.min.css" />
  </head>
  <body>
    <div id="graphiql">Loading Universal GraphiQL...</div>
    <script src="https://unpkg.com/graphiql@1.4.2/graphiql.min.js"></script>
    <script>
      function graphQLFetcher(graphQLParams) {
        // Headers are passed via the UI
        let headers = {
          'Content-Type': 'application/json',
        };
        return fetch(window.location.href, {
          method: 'post',
          headers: headers,
          body: JSON.stringify(graphQLParams),
        }).then(function (response) {
          return response.json();
        });
      }

      ReactDOM.render(
        React.createElement(GraphiQL, {
          fetcher: graphQLFetcher,
          defaultVariableEditorOpen: true,
          headerEditorEnabled: true, // This enables the header tab
        }),
        document.getElementById('graphiql'),
      );
    </script>
  </body>
</html>
"""
