import DocsLayout from '@/components/docs/DocsLayout';

export default function ApiDocsPage() {
  return (
    <DocsLayout title="REST API Reference">
      <section className="mb-10">
        <h2 className="text-2xl font-bold mb-4">Overview</h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          The Aegis Cloud API is a RESTful interface that allows you to programmatically interact with your fleet, execute tasks, and retrieve telemetry data. All API endpoints are authenticated using Bearer tokens.
        </p>
        <div className="bg-secondary/50 rounded-lg p-4 font-mono text-sm my-4 border border-border">
          Base URL: https://api.aegiscloud.in/api/v1
        </div>
      </section>

      <section className="mb-10">
        <h2 className="text-2xl font-bold mb-4">Authentication</h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          To authenticate with the API, you must provide a valid API key in the <code>Authorization</code> header of your HTTP requests.
        </p>
        <div className="bg-black rounded-lg p-4 font-mono text-sm my-4 border border-border overflow-x-auto text-green-400">
          Authorization: Bearer aegis_live_xxxxxxxxx
        </div>
      </section>

      <section className="mb-10">
        <h2 className="text-2xl font-bold mb-6 border-b border-border pb-2">Endpoints</h2>
        
        {/* Endpoint 1 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs font-bold font-mono">GET</span>
            <code className="text-lg font-semibold">/devices</code>
          </div>
          <p className="text-muted-foreground mb-3">Retrieves a paginated list of all devices enrolled in your organization.</p>
          <div className="bg-black rounded-lg p-4 font-mono text-sm border border-border overflow-x-auto text-gray-300">
            curl -X GET "https://api.aegiscloud.in/api/v1/devices" \<br/>
            &nbsp;&nbsp;-H "Authorization: Bearer $API_KEY"
          </div>
        </div>

        {/* Endpoint 2 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-bold font-mono">POST</span>
            <code className="text-lg font-semibold">/tasks/execute</code>
          </div>
          <p className="text-muted-foreground mb-3">Dispatches a new automation task to one or more devices.</p>
          <div className="bg-black rounded-lg p-4 font-mono text-sm border border-border overflow-x-auto text-gray-300">
            {`curl -X POST "https://api.aegiscloud.in/api/v1/tasks/execute" \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "devices": ["DEV-001", "DEV-002"],
    "command": "clean_temp",
    "timeout": 60
  }'`}
          </div>
        </div>
        
        {/* Endpoint 3 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <span className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs font-bold font-mono">WS</span>
            <code className="text-lg font-semibold">/ws/telemetry</code>
          </div>
          <p className="text-muted-foreground mb-3">Connects to the real-time WebSocket firehose for live device metrics.</p>
          <p className="text-sm text-muted-foreground italic">Requires specialized WebSocket client libraries configured with Bearer authentication.</p>
        </div>
      </section>
    </DocsLayout>
  );
}
