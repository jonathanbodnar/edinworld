import LeftPanel from '../components/left/LeftPanel'
import CenterPanel from '../components/center/CenterPanel'
import RightPanel from '../components/right/RightPanel'

export default function ThreePanelLayout() {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'var(--left-width) 1fr var(--right-width)',
      height: '100vh',
      width: '100vw',
      overflow: 'hidden',
    }}>
      <LeftPanel />
      <CenterPanel />
      <RightPanel />
    </div>
  )
}
