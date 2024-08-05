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
            <button className='desktop'>export</button>
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
            <div className='top-words'>
              {/* Technically, you aren't supposed to use indexes, 
                  but, there are no deletes allowed so this should be fine 
                  ACTUALLY: This should use the original idx, from the original
                  list or it will have changing idx
                  */}
              {getTopKTexts(10, 20).map((x, i) =>
                <WordLine key={i} word={x.text} score={x.score} />
                // <Fragment key={i}>
                //   <p>{x} {}</p>
                // </Fragment>
              )}
              {/* <h3>General Stats</h3> */}
              {/* <p>words submitted: {textScorePairs.length}</p>
            <p>average novelty: {calcAverageNovelty()}</p> */}
            </div>

          </div>
        </div>
        {/* 
        stats
        top words
        words submimtted
        average novelty
        */}
      </main>
    </>
  )
}

export default App
