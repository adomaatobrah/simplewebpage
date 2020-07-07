function generate(data) {
    let results = data.results

    d3.select(".results").html("")
    .append("div")
        .attr("id", "colored_output")

    for (i = 0; i < results.length; i++) {
        d3.select("#colored_output")
        .append("span")
            .text(results[i][0])
            .attr("title", `${results[i][1]} - ${results[i][2]} => ${results[i][3]}`)
            //.attr("style", "background-color:" + colors[i][1] + ";font-size:150%;");
    }
}

async function getData() {
    let text = document.getElementById("text");

    var entry = {
        text: text.value,
    };

    let response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        mode: "cors",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    });

    let data = await response.json()

    generate(data);
}