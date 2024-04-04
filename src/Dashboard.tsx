import React, { Component } from "react";
import {Link} from "react-router-dom";
import {Bar, Pie} from "react-chartjs-2";
import {
    Chart as ChartJS,
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import {CardDescriptor, DailySummary, EASINESS_DAYS, Language} from "./models";

ChartJS.register(
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const easinessColor = (easiness: number) => `hsl(${easiness*35}, 80%, 80%)`;

function getUTCToday() {
    const today = new Date();
    today.setUTCHours(0);
    today.setUTCMinutes(0);
    today.setUTCSeconds(0);
    today.setMilliseconds(0);
    return today;
}

const millisecondsInDay = 1000*60*60*24;

function addDays(d: Date, days: number) {
    return new Date(d.getTime() + days*millisecondsInDay);
}

function ProjectionBarChart(props: {card_descriptors: CardDescriptor[]}) {
    const {card_descriptors} = props;

    const today = getUTCToday();
    const lookahead = 30;
    const days = Array.from(Array(lookahead).keys()).map(n => addDays(today, n + 1));

    const labels = days.map(d => `${d.getUTCMonth() + 1}-${d.getUTCDate()}`)

    const datasets = EASINESS_DAYS.map((num_days, easiness) => ({
        label: `After ${num_days} days`,
        data: days.map(d => card_descriptors.filter(c => ((c.last_trial?.easiness === easiness) && (c.due_date.getTime() === d.getTime()))).length),
        backgroundColor: easinessColor(easiness),
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
        },
    }}/>;
}

function EasinessPieChart(props: {card_descriptors: CardDescriptor[]}) {
    const { card_descriptors } = props;

    const labels = EASINESS_DAYS.map(days => `${days} days`);
    const colors = EASINESS_DAYS.map((_, easiness) => easinessColor(easiness));
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

type ModalType = "details" | "history" | "share";

type Props = {
    is_superuser: boolean,
    current_language: Language,
}

type State = {
    card_descriptors?: CardDescriptor[],
    modal_type: ModalType | null,
    history?: DailySummary[],
}

export default class Dashboard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            modal_type: null,
        };
    }

    componentDidMount() {
        fetch(`/api/playing_lemmas?language_id=${this.props.current_language.id}`)
            .then(res => res.json())
            .then(data => this.setState({card_descriptors: data.map((descriptor: any) => ({
                    ...descriptor,
                    due_date: new Date(descriptor.due_date),
                }))}))
    }

    closeX() {
        return (
            <div className="close" onClick={() => this.setState({modal_type: null})}>
                X
            </div>
        );
    }

    cardDetailPane() {
        const {card_descriptors} = this.state;

        if (card_descriptors === undefined) {
            return null;
        }

        return (
            <div className="dashboard-modal">
                <div className="container">
                    <div className="row">
                        {this.closeX()}
                        <div className="col-12">
                            <ProjectionBarChart card_descriptors={card_descriptors}/>
                        </div>
                        <div className="col-12" style={{display: "flex"}}>
                            <div style={{margin: "auto", height: "40vh"}}>
                                <EasinessPieChart card_descriptors={card_descriptors}/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    historyModal() {
        const { history } = this.state;

        if (history === undefined) {
            fetch(`/api/history?language_id=${this.props.current_language.id}`)
                .then(res => res.json())
                .then(data => this.setState({
                    history: data.map((summary: any) => ({...summary, date: new Date(summary.date)}))
                }))
            return null;
        }

        const totalCards = history.reduce(
            (total, summary) => (total + summary.new_lemma_trials + summary.review_trials),
            0,
        )

        return (
            <div className="dashboard-modal">
                <div className="container">
                    <div className="row">
                        {this.closeX()}
                        <div className="col-12">
                            <h2>Your history</h2>
                        </div>
                        <div className="col-12">
                            <p style={{textAlign: "center"}}>In total, you've done {totalCards} cards.</p>
                        </div>

                        <div className="col-2"><p>Date</p></div>
                        <div className="col-2"><p>New words</p></div>
                        <div className="col-2"><p>New word cards</p></div>
                        <div className="col-2"><p>Review cards</p></div>
                        <div className="col-4"><p>Total cards</p></div>

                        {history.map(summary => (
                            <>
                                <div className="col-2">
                                    <p>{summary.date.getUTCFullYear()}-{summary.date.getUTCMonth() + 1}-{summary.date.getUTCDate()}</p>
                                </div>
                                <div className="col-2">
                                    <p>{summary.new_lemmas}</p>
                                </div>
                                <div className="col-2">
                                    <p>{summary.new_lemma_trials}</p>
                                </div>
                                <div className="col-2">
                                    <p>{summary.review_trials}</p>
                                </div>
                                <div className="col-4">
                                    <p>{summary.new_lemma_trials + summary.review_trials}</p>
                                </div>
                            </>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    modal() {
        switch (this.state.modal_type) {
            case "details":
                return this.cardDetailPane();
            case "history":
                return this.historyModal();
            case "share":
                return null;
            case null:
                return null;
        }
    }

    render() {
        const {card_descriptors} = this.state;

        if (card_descriptors === undefined) {
            return null;
        }

        const new_cards = card_descriptors.filter(card => card.last_trial === null)
        const seen_cards = card_descriptors.filter(card => card.last_trial !== null)
        const now = new Date();
        const due_cards = seen_cards.filter(card => card.due_date < now);

        return (
            <div className="col-12 col-md-6 offset-md-3">
                <div className="row">
                    <div className="col-12">
                        <p>
                            Learning {seen_cards.length}/{card_descriptors.length} added words.
                            {' '}{due_cards.length} cards ready for review.
                        </p>
                    </div>
                    {(due_cards.length > 0) ? (
                        <div className="col-6">
                            <Link to="/cards/review">
                                <div className="big button">
                                    Review cards
                                </div>
                            </Link>
                        </div>
                    ) : (
                        <div className="col-6">
                            <div className="big button" onClick={() => this.setState({modal_type: "share"})}>
                                Share today's reviews!
                            </div>
                        </div>
                    )}
                    <div className="col-6">
                        <Link to="/cards/new">
                            <div className="big button">
                                Learn new cards
                            </div>
                        </Link>
                    </div>
                    <div className="col-6">
                        <div className="big button" onClick={() => this.setState({modal_type: "details"})}>
                            Show details
                        </div>
                    </div>
                    <div className="col-6">
                        <div className="big button" onClick={() => this.setState({modal_type: "history"})}>
                            See history
                        </div>
                    </div>
                    <div className="col-12">
                        <p>
                            domcumints
                        </p>
                    </div>
                    <div className="col-6">
                        <Link to="/collections">
                            <div className="big button">
                                See collections
                            </div>
                        </Link>
                    </div>
                    {this.modal()}
                </div>
            </div>
        );
    }
}
