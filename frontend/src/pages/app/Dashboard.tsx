import { FolderKanban, Plus } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Badge, statusTone } from "../../components/Badge";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { EmptyState } from "../../components/EmptyState";
import { Spinner } from "../../components/Spinner";
import { casesApi, type Schemas } from "../../lib/apiClient";

export function Dashboard() {
  const [cases, setCases] = useState<Schemas["CaseOut"][] | null>(null);
  const [showNewCase, setShowNewCase] = useState(false);
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);

  function reload() {
    casesApi.list().then(setCases);
  }

  useEffect(reload, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreating(true);
    try {
      await casesApi.create({ title });
      setTitle("");
      setShowNewCase(false);
      reload();
    } finally {
      setCreating(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Cases</h1>
        <Button onClick={() => setShowNewCase((v) => !v)}>
          <Plus className="h-4 w-4" aria-hidden />
          New Case
        </Button>
      </div>

      {showNewCase && (
        <Card className="mt-4">
          <form onSubmit={handleCreate} className="flex items-end gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-700" htmlFor="title">
                Case title
              </label>
              <input
                id="title"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <Button type="submit" disabled={creating}>
              {creating ? "Creating…" : "Create"}
            </Button>
          </form>
        </Card>
      )}

      <div className="mt-6">
        {cases === null ? (
          <Spinner label="Loading cases…" />
        ) : cases.length === 0 ? (
          <EmptyState
            icon={FolderKanban}
            title="No cases yet"
            description="Create your first case to start uploading documents."
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cases.map((c) => (
              <Link key={c.id} to={`/app/cases/${c.id}`}>
                <Card className="h-full transition-shadow hover:shadow-md">
                  <h3 className="font-semibold text-slate-900">{c.title}</h3>
                  <div className="mt-3">
                    <Badge tone={statusTone(c.status)}>{c.status}</Badge>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
