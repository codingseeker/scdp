import { useState } from 'react'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import SearchPage from './pages/SearchPage'
import EntityPage from './pages/EntityPage'
import SearchBar from './components/SearchBar'
import HealthBadge from './components/HealthBadge'

function HeaderSearch() {
  const navigate = useNavigate()
  const handleSearch = (q) => navigate(`/?q=${encodeURIComponent(q)}`)
  return <SearchBar onSearch={handleSearch} size="sm" />
}

function Header() {
  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 flex items-center gap-4 py-2.5">
        <div className="flex items-center gap-2 flex-shrink-0 min-w-0">
          <div className="w-7 h-7 rounded bg-slate-900 flex items-center justify-center flex-shrink-0">
            <span className="text-[10px] font-bold text-white">SC</span>
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-slate-900 leading-tight whitespace-nowrap">
              Supply Chain Intelligence
            </div>
            <div className="text-[10px] text-slate-400 leading-tight">Investigation Console</div>
          </div>
        </div>
        <div className="flex-1 max-w-xl ml-2">
          <HeaderSearch />
        </div>
        <div className="flex-shrink-0 hidden sm:block">
          <HealthBadge />
        </div>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/entity/:id" element={<EntityPage />} />
            <Route path="*" element={<SearchPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
