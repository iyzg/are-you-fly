import flySVG from '../assets/fly.svg'

const About = (props) => {
    return (
        <div className="about">
            <h2 className="about-title">
                Scoring creativity from a fly
            </h2>
            <p>
                How Fly Are You? uses an embedding model and   
                &nbsp;<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6304992/">fly-inspired bloom filter</a>&nbsp; 
                to score the creativity of your text. Over time, things that were once
                "boring" become novel again to our digital fly. You can submit any text, and the fly will return a score between 0 (least creative) to 100 (most creative)!
            </p>
            <p>
                <strong>How &ldquo;fly&rdquo; are you compared to the rest of the internet?</strong>
            </p>
            <img src={flySVG} className='fly-logo'/>
        </div>
    )
}

export default About