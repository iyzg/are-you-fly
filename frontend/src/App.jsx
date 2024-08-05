import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Header from './components/header'
import About from './components/about'

function App() {
  const [text, setText] = useState('')
  const [resText, setResText] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    // console.log('submitted: ', text)

    try {
      const res = await fetch('https://howflyareyou.com/api/novelty', {
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
      // console.log('returned novelty: ', data.result)
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
      <Header />
      <main>
        <About />
        <form onSubmit={handleSubmit} className='submitForm'>
          <input placeholder='Send text off to the fly!' value={text} onChange={handleTextChange} />
            <button type="submit">submit</button>
        </form>
        <p>{resText}</p>
        {/* <div className='stats'>
          <h2>Stats (WIP)</h2> 
        </div> */}
      </main>
    </>
  )
}

export default App
