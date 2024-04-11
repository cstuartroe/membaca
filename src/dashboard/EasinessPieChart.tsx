import {CommonCardDescriptor, EASINESS_DAYS} from "../models";
import {ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Title, Tooltip} from "chart.js";
import {Pie} from "react-chartjs-2";
import React from "react";

import {EASINESS_COLORS} from "./shared";

ChartJS.register(
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

export default function EasinessPieChart(props: {card_descriptors: CommonCardDescriptor[]}) {
    const { card_descriptors } = props;

    const labels = EASINESS_DAYS.map(days => `${days} days`);
    const colors = EASINESS_DAYS.map((_, easiness) => EASINESS_COLORS[easiness]);
    const data = EASINESS_DAYS.map((_, easiness) => card_descriptors.filter(c => c.last_trial?.easiness === easiness).length);

    const dataset = {
        labels,
        datasets: [
            {
                label: '# of Words',
                data,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 0,
            },
        ],
    };

    return <Pie data={dataset} options={{
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: 'Easiness of words',
            },
        },
    }}/>;
}
