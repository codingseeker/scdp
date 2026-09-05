import { useState } from 'react'

export default function SearchBar({ onSearch, initialValue = '', autoFocus = false, size = 'lg' }) {
  const [value, setValue] = useState(initialValue)

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = value.trim()
    if (trimmed) onSearch(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full gap-2" role="search">
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search suppliers, countries, or categories…"
        autoFocus={autoFocus}
        className={`input-field flex-1 ${size === 'lg' ? 'py-2.5 px-4 text-base' : 'py-1.5 px-3 text-sm'}`}
      />
      <button type="submit" className="btn-primary flex-shrink-0 px-4">
        Search
      </button>
    </form>
  )
}
