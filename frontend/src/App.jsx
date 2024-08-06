import { Fragment, useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import chartSVG from './assets/chart.svg'
import exportSVG from './assets/export.svg'
import sentSVG from './assets/sent.svg'
import './App.css'
import Header from './components/header'
import About from './components/about'
import WordLine from './components/word-line'
import Circles from './components/circles'
import LinePlot from './components/line-plot'

function App() {
  const storedTextScorePairs = JSON.parse(localStorage.getItem('textScorePairs')) || []

  const [text, setText] = useState('')
  const [resText, setResText] = useState('')
  const [textScorePairs, setTextScorePairs] = useState(storedTextScorePairs)

  // Store things into local storage
  useEffect(() => {
    localStorage.setItem('textScorePairs', JSON.stringify(textScorePairs))
  }, [textScorePairs])

  const handleSubmit = async (event) => {
    event.preventDefault()

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
      // setResText(text + ' novelty: ' + data.result)
      setTextScorePairs([...textScorePairs, { text, score: data.result }])
      // setTextScorePairs(textScorePairs.concat({ text, score: data.result }))
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const handleTextChange = (event) => {
    setText(event.target.value)
  }

  const calcAverageNovelty = () => {
    const len = textScorePairs.length
    const sum = textScorePairs.reduce((partial, x) => partial + x.score, 0.0) 
    if (len === 0) {
      return 0
    } else {
      return (sum / len).toFixed(2)
    }
  }

  // Return top n words, also trunacate to some length
  const getTopKTexts = (k, len) => {
    let sortedPairs = textScorePairs.toSorted((a, b) => b.score - a.score)  
    // Return object of text and score
    return sortedPairs.slice(0, k).map(x => ({text: x.text.slice(0, len), score: x.score}))
  }

  return (
    <>
      <Header />
      <main>
        <About />
        <form onSubmit={handleSubmit} className='submitForm'>
          <input className='textinput' placeholder='Send text off to the fly!' value={text} onChange={handleTextChange} />
            <button type="submit">submit</button>
        </form>
        <p>{resText}</p>
        <div className='stats'>
          <div className='stats-header'>
            <h2>Stats</h2>
            <img src={exportSVG} className='desktop mini-export'></img>
          </div>
          <div className='stats-box'>
            <div className='general-stats'>
              <div className='stat-line'>
                <img src={sentSVG}></img> {textScorePairs.length}
              </div>
              <div className='stat-line'>
                <img src={chartSVG}></img> {calcAverageNovelty()}
              </div>
              <div className='stat-line'>
                <img src={exportSVG} className='mobile'></img>
              </div>
              {/* <button>export</button> */}
            </div>
            {/* Change this to line chart */}
            <div className='line-plot'>
              {/* <Circles /> */}
              <LinePlot textScorePairs={textScorePairs}/>
            </div>

          </div>
        </div>
        <div className='log'>
          <div className='log-header'>
            <h2>Log</h2>
          </div>
          <div className='log-box'>
            {textScorePairs.toReversed().slice(0, 50).map((x, i) => 
              <div key={i} className='log-item'>
                <span className='log-item-text'>
                  {x.text}
                </span>
                <span>
                  {x.score}
                </span>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export default App
