export function chartTheme() {
  const style = getComputedStyle(document.documentElement)
  return {
    grid: style.getPropertyValue('--chart-grid').trim() || 'rgba(0,0,0,0.08)',
    line: style.getPropertyValue('--chart-line').trim() || '#007aff',
    tooltipBg: style.getPropertyValue('--chart-tooltip-bg').trim() || '#ffffff',
    tooltipBorder: style.getPropertyValue('--chart-tooltip-border').trim() || 'rgba(0,0,0,0.08)',
    tick: style.getPropertyValue('--text-secondary').trim() || '#6e6e73',
  }
}
