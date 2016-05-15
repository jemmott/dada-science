# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:15:02 2014
CWJ for Embarke
"""

def header():
    html = """<!DOCTYPE html>
<meta charset="utf-8">
<body>
<script src="../lib/d3/d3.js"></script>
<script src="../d3.layout.cloud.js"></script>
<script>
  
  var words = """
      
    return html

def footer():
    html = """;
    
  d3.layout.cloud().size([1280, 800])
      .words(words)
      .padding(5)
      .rotate(0)
      .font("Impact")
      .fontSize(function(d) { return d.size; })
      .on("end", draw)
      .start();


  function draw(words) {
    d3.select("body").append("svg")
        .attr("width", 1280)
        .attr("height", 800)
      .append("g")
        .attr("transform", "translate(640,400)")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
        .style("fill", "steelblue")
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });
  }
</script>
"""
    return html
