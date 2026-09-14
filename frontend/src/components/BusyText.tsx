type BusyTextProps = {
  idle: string
  busy: string
  isBusy: boolean
}

export function BusyText({
  idle,
  busy,
  isBusy,
}: BusyTextProps) {
  if (!isBusy) {
    return idle
  }

  return (
    <>
      {busy}
      <span className="busy-dots" aria-hidden="true">
        <span>.</span>
        <span>.</span>
        <span>.</span>
      </span>
    </>
  )
}
