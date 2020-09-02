function getPieData(data) {
    let colors = [
        "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
        "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
        "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"
    ]
    pieData = []

    for (let key in data) {
        if (key !== 'total' && key !== 'percent') {
            colorIDX = Math.floor(Math.random() * colors.length)
            pieData.push({
                value: data[key],
                label: key,
                color: colors[colorIDX]
            })
            colors.splice(colorIDX, 1)

        }
    }

    return pieData

}