# API Reference

Interactive reference generated from the backend's own OpenAPI schema, so it can never drift from what the API actually does. The running backend also serves this live at `/docs` and the raw schema at `/openapi.json`; the copy below is a static snapshot for the docs site.

To refresh the snapshot after an API change:

```
curl http://localhost:8000/openapi.json -o docs/api/openapi.json
```

<div id="swagger-ui"></div>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
  window.onload = function() {
    SwaggerUIBundle({
      url: "openapi.json",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis],
    });
  };
</script>
