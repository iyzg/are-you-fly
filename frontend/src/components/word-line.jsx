const WordLine = ({ word, score }) => {
    return (
        <>
            <p className='top-word' style={{width: `calc(${score / 100 * 0.8} * 100%)`}}>{word} { }</p>
            
        </>
    )
}

export default WordLine 