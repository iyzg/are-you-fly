import { useEffect, useRef } from 'react'
import * as d3 from "d3";

const LinePlot = ({ 
    textScorePairs,
    width = 100,
    height = 50,
    marginTop = 2,
    marginRight = 2,
    marginBottom = 2,
    marginLeft = 2 
}) => {

    // const margin = {top: 5, right: 10, bottom: 5, left: 10},
    //       width = 100 - margin.left - margin.right,
    //       height = 50 - margin.top - margin.bottom;

    // useEffect(() => {
    //     console.log('updating line plot')
        // const svgElement = d3.select(ref.current)
        //     .append("svg")
            // .attr("width", width + margin.left + margin.right)
            // .attr("height", height + margin.top + margin.bottom)
            // .append("g")
            // .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



        // svgElement.append("path")
        //     .datum(textScorePairs)
        //     .attr("fill", "none")
        //     .attr("stroke", "steelblue")
        //     .attr("stroke-width", 0.5)
        //     .attr("d", d3.line()
        //         .x((_, i) => x(i))
        //         .y((d) => y(d.score))
        //     )

    // }, [textScorePairs])


    let x = d3.scaleLinear()
        .domain([0, textScorePairs.length - 1])
        .range([ marginLeft, width - marginRight])

    let y = d3.scaleLinear()
        .domain([0, 100])
        .range([ height - marginBottom, marginTop ])

    const line = d3.line()
        .x((_, i) => x(i))
        .y((d) => y(d.score))
        .curve(d3.curveMonotoneX)

    return (
        <svg
            viewBox={`0 0 ${width} ${height}`}
            // width={width}
            // height={height}
        >
            <path
                fill="none"
                stroke="#B85B01"
                strokeWidth="0.4"
                d={line(textScorePairs)}
            />
        </svg>
    )
}

export default LinePlot