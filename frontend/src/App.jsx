import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [resText, setResText] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    console.log('submitted: ', text)

    try {
      const res = await fetch('http://howflyareyou.com/api/novelty', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      })

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await res.json()
      console.log('returned novelty: ', data.result)
      setResText('Novelty: ' + data.result)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const handleTextChange = (event) => {
    setText(event.target.value)
  }

  return (
    <>
      <h1>How fly are you?</h1>
      <form onSubmit={handleSubmit}>
        <div>
          text: <input value={text} onChange={handleTextChange} />
        </div>
        <div>
          <button type="submit">submit</button>
        </div>
        <p>{resText}</p>
      </form>
    </>
  )
}

export default App
