import {CommonCardDescriptor, EASINESS_DAYS} from "../models";
import {ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Title, Tooltip} from "chart.js";
import {Bar} from "react-chartjs-2";
import React from "react";

import {getUTCToday, addDays, EASINESS_COLORS} from "./shared";

ChartJS.register(
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

export default function ProjectionBarChart(props: {card_descriptors: CommonCardDescriptor[]}) {
    const {card_descriptors} = props;

    const today = getUTCToday();
    const lookahead = 30;
    const days = Array.from(Array(lookahead).keys()).map(n => addDays(today, n + 1));

    const labels = days.map(d => `${d.getUTCMonth() + 1}-${d.getUTCDate()}`)

    const datasets = EASINESS_DAYS.map((num_days, easiness) => ({
        label: `After ${num_days} days`,
        data: days.map(d => card_descriptors.filter(c => ((c.last_trial?.easiness === easiness) && (c.due_date.getTime() === d.getTime()))).length),
        backgroundColor: EASINESS_COLORS[easiness],
    }))

    return <Bar data={{labels, datasets}} options={{
        responsive: true,
        aspectRatio: 3.5,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: 'Projected words due',
            },
        },
        scales: {
            x: {
                stacked: true,
            },
            y: {
                stacked: true,
            },
        },
    }}/>;
}
