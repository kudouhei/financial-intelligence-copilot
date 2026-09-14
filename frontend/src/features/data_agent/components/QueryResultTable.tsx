import type { SqlQueryResult } from '../types'

type QueryResultTableProps = {
  result: SqlQueryResult
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) {
    return '—'
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}

export function QueryResultTable({
  result,
}: QueryResultTableProps) {
  return (
    <section className="query-results">
      <div className="query-results-heading">
        <h3>Query results</h3>

        <span>
          {result.row_count}{' '}
          {result.row_count === 1 ? 'row' : 'rows'}
          {result.truncated ? ' · truncated' : ''}
        </span>
      </div>

      <div
        className="query-table-wrapper"
        role="region"
        aria-label="SQL query results"
        tabIndex={0}
      >
        <table>
          <thead>
            <tr>
              {result.columns.map((column) => (
                <th key={column} scope="col">
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {result.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {result.columns.map((column) => (
                  <td key={column}>
                    {formatCell(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}