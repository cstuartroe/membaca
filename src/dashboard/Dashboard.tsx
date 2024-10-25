import React, { Component } from "react";
import {Link} from "react-router-dom";
import {
    CardDescriptor,
    DailySummary,
    Language,
    Trial,
    Document,
    MetadataCardDescriptor,
    CommonCardDescriptor, MetadataPlaySummary,
} from "../models";
import {ISODate} from "./shared";
import ProjectionBarChart from "./ProjectionBarChart";
import EasinessPieChart from "./EasinessPieChart";

const DutchLanguageId = 1;

const metadataFields: {[language_id: number]: string[]} = {
    [DutchLanguageId]: ["gender"],
}

type CEFRLevel = {
    name: string,
    lemmas: number,
}

const _cl = (name: string, lemmas: number) => ({name, lemmas});

const CEFRLevels: CEFRLevel[] = [
    _cl("A0", 250),
    _cl("A1", 750),
    _cl("A2", 1500),
    _cl("B1", 3000),
    _cl("B2", 6000),
    _cl("C1", 10000),
    _cl("C2", 12000),
]

type ModalType = "details" | "history" | "share" | "reading_history" | "gender_details" | "gender_history";

type History = {
    summaries: DailySummary[],
    today: {
        new_lemma_trials: Trial[],
        review_trials: Trial[],
    },
}

type DocumentHistory = {
    last_read: Date,
    sentences_read: number,
    total_sentences: number,
    document: Document,
}

type WordsOnDay = {
    date: Date,
    words: number,
    new_lemmas: number,
    added_lemmas: number,
}

type ReadingHistory = {
    document_histories: DocumentHistory[],
    words_read_by_day: WordsOnDay[],
}

type Props = {
    is_superuser: boolean,
    current_language: Language,
}

type State = {
    card_descriptors?: CardDescriptor[],
    metadata_play_summaries: {
        [metadata_field: string]: MetadataPlaySummary,
    },
    modal_type: ModalType | null,
    history?: History,
    reading_history?: ReadingHistory,
    metadata_history: {
        [metadata_field: string]: DailySummary[],
    },
}

export default class Dashboard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            modal_type: null,
            metadata_play_summaries: {},
            metadata_history: {},
        };
    }

    componentDidMount() {
        fetch(`/api/playing_lemmas?language_id=${this.props.current_language.id}`)
            .then(res => res.json())
            .then(data => this.setState({card_descriptors: data.map((descriptor: any) => ({
                    ...descriptor,
                    due_date: new Date(descriptor.due_date),
                }))}));

        (metadataFields[this.props.current_language.id] || []).forEach((field) => {
            fetch(`/api/playing_metadata?language_id=${this.props.current_language.id}&metadata_field=${field}`)
                .then(res => res.json())
                .then(data => this.setState({
                    metadata_play_summaries: {
                        ...this.state.metadata_play_summaries,
                        [field]: {
                            ...data,
                            playing_metadata: data.playing_metadata.map((descriptor: any) => ({
                                ...descriptor,
                                due_date: new Date(descriptor.due_date),
                            })),
                        },
                    }
                }));
        })
    }

    getHistory() {
        if (this.state.history !== undefined) {
            return this.state.history;
        }

        fetch(`/api/history?language_id=${this.props.current_language.id}`)
            .then(res => res.json())
            .then(data => this.setState({
                history: {
                    summaries: data.summaries.map((summary: any) => ({...summary, date: new Date(summary.date)})),
                    today: data.today,
                }
            }))
        return null;
    }

    getReadingHistory() {
        if (this.state.reading_history !== undefined) {
            return this.state.reading_history;
        }

        fetch(`/api/reading_history?language_id=${this.props.current_language.id}`)
            .then(res => res.json())
            .then(data => this.setState({
                reading_history: {
                    document_histories: data.document_histories.map((h: any) => ({...h, last_read: new Date(h.last_read)})),
                    words_read_by_day: data.words_read_by_day.map((d: any) => ({...d, date: new Date(d.date)})),
                }
            }))
        return null;
    }

    getMetadataHistory(metadata_field: string) {
        if (this.state.metadata_history[metadata_field] !== undefined) {
            return this.state.metadata_history[metadata_field];
        }

        fetch(`/api/metadata_history?language_id=${this.props.current_language.id}&metadata_field=${metadata_field}`)
            .then(res => res.json())
            .then(data => this.setState({
                metadata_history: {
                    [metadata_field]: data.summaries.map((summary: any) => ({...summary, date: new Date(summary.date)})),
                }
            }))
        return null;
    }

    closeX() {
        return (
            <div className="close" onClick={() => this.setState({modal_type: null})}>
                X
            </div>
        );
    }

    genericCardDetailPane(card_descriptors: undefined | CommonCardDescriptor[]) {
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

    cardDetailPane() {
        return this.genericCardDetailPane(this.state.card_descriptors);
    }

    metadataCardDetailPane(metadata_field: string) {
        return this.genericCardDetailPane(this.state.metadata_play_summaries[metadata_field].playing_metadata);
    }

    genericHistoryModal(summaries: DailySummary[]) {
        const totalCards = summaries.reduce(
            (total, summary) => (total + summary.new_lemma_trials + summary.review_trials),
            0,
        )

        return (
            <div className="dashboard-modal">
                <div className="container">
                    <div className="row">
                        {this.closeX()}
                        <div className="col-12">
                            <h2>Your flashcard history</h2>
                        </div>
                        <div className="col-12">
                            <p style={{textAlign: "center"}}>In total, you've done {totalCards} cards.</p>
                        </div>

                        <div className="col-2"><p>Date</p></div>
                        <div className="col-2"><p>New words</p></div>
                        <div className="col-2"><p>New word cards</p></div>
                        <div className="col-2"><p>Review cards</p></div>
                        <div className="col-2"><p>Total cards</p></div>
                        <div className="col-2"><p>Time taken</p></div>
                    </div>

                    {summaries.map(summary => (
                        <div className="row" key={summary.date.getTime()}>
                            <div className="col-2">
                                <p>{ISODate(summary.date)}</p>
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
                            <div className="col-2">
                                <p>{summary.new_lemma_trials + summary.review_trials}</p>
                            </div>
                            <div className="col-2">
                                <p>
                                    {(Math.floor(summary.seconds_taken / 60) + "").padStart(2, '0')}
                                    :{(Math.round(summary.seconds_taken % 60) + "").padStart(2, '0')}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    historyModal() {
        const history = this.getHistory();

        if (history === null) {
            return null;
        }

        return this.genericHistoryModal(history.summaries);
    }

    metadataHistoryModal(metadata_field: string) {
        const summaries = this.getMetadataHistory(metadata_field);

        if (summaries === null) {
            return null;
        }

        return this.genericHistoryModal(summaries);
    }

    shareModal() {
        const history = this.getHistory();

        if (history === null) {
            return null;
        }

        const row_size = 5;

        const headline = `I finished all my ${this.props.current_language.name} reviews today!`;
        const num_trials = history.today.review_trials.length;

        let squares: (string | React.ReactNode)[] = [];
        let correct = 0;
        let copy_string = headline + "\n";

        history.today.review_trials.forEach((trial, i) => {
            if (i !== 0 && i % row_size === 0) {
                squares.push(<br key={i}/>);
                copy_string += "\n";
            }
            const square = trial.correct ? "🟩" : "🟥";
            squares.push(square);
            copy_string += square;
            if (trial.correct) { correct++; }
        })

        const fractions = `${correct}/${num_trials} (${Math.round(100*correct/history.today.review_trials.length)}%)`;
        copy_string += "\n" + fractions;

        return (
            <div className="dashboard-modal">
                <div className="container">
                    <div className="row">
                        {this.closeX()}
                        <div className="col-8 col-md-4 offset-2 offset-md-4">
                            <p>
                                {headline}
                                <br/>
                                {squares}
                                <br/>
                                {fractions}
                            </p>
                            <div
                                className="big button"
                                onClick={() => navigator.clipboard.writeText(copy_string)}
                            >
                                Copy!
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    readingHistoryModal() {
        const reading_history = this.getReadingHistory();

        if (reading_history === null) {
            return null;
        }

        return (
            <div className="dashboard-modal">
                <div className="container">
                    <div className="row">
                        {this.closeX()}
                        <div className="col-12">
                            <h2>Your reading history</h2>
                        </div>

                        <div className="col-2"><p>Date</p></div>
                        <div className="col-2"><p>Words read</p></div>
                        <div className="col-2"><p>New lemmas</p></div>
                        <div className="col-2"><p>Percent new</p></div>
                        <div className="col-2"><p>Added lemmas</p></div>
                        <div className="col-2"><p>New/added ratio</p></div>
                    </div>

                    {reading_history.words_read_by_day.map(day => (
                        <div className="row" key={day.date.getTime()}>
                            <div className="col-2">
                                <p>{ISODate(day.date)}</p>
                            </div>
                            <div className="col-2">
                                <p>{day.words}</p>
                            </div>
                            <div className="col-2">
                                <p>{day.new_lemmas}</p>
                            </div>
                            <div className="col-2">
                                <p>{Math.round(1000 * day.new_lemmas / day.words)/10}%</p>
                            </div>
                            <div className="col-2">
                                <p>{day.added_lemmas}</p>
                            </div>
                            <div className="col-2">
                                <p>{Math.round(100 * day.added_lemmas / day.new_lemmas)/100}</p>
                            </div>
                        </div>
                    ))}
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
                return this.shareModal();
            case "reading_history":
                return this.readingHistoryModal();
            case "gender_details":
                return this.metadataCardDetailPane("gender");
            case "gender_history":
                return this.metadataHistoryModal("gender")
            case null:
                return null;
        }
    }

    metadataSections() {
        if (this.props.current_language.name === "Dutch") {
            const gender_play_summary = this.state.metadata_play_summaries["gender"];

            if (gender_play_summary === undefined) {
                return null;
            }

            const gender_card_descriptors = gender_play_summary.playing_metadata;

            const seen_cards = gender_card_descriptors.filter(card => card.last_trial !== null);
            const now = new Date();
            const due_cards = seen_cards.filter(card => card.due_date < now);

            return <>
                <div className="col-12">
                    <p>
                        Learning gender for {seen_cards.length}/{gender_card_descriptors.length} added words.
                        {' '}{due_cards.length} cards ready for review.{' '}
                        {gender_play_summary.not_playable} lemmas are not gendered.{' '}
                        {gender_play_summary.unannotated} lemmas still lack gender annotation.
                    </p>
                </div>
                <div className="col-6">
                    <Link to="/metadata_cards/review?metadata_field=gender">
                        <div className="big button">
                            Review genders
                        </div>
                    </Link>
                </div>
                <div className="col-6">
                    <Link to="/metadata_cards/new?metadata_field=gender">
                        <div className="big button">
                            Learn gender of new nouns
                        </div>
                    </Link>
                </div>
                <div className="col-6">
                    <div className="big button" onClick={() => this.setState({modal_type: "gender_details"})}>
                        Show details
                    </div>
                </div>
                <div className="col-6">
                    <div className="big button" onClick={() => this.setState({modal_type: "gender_history"})}>
                        See history
                    </div>
                </div>
            </>;
        } else {
            return null;
        }
    }

    render() {
        const {card_descriptors} = this.state;

        if (card_descriptors === undefined) {
            return null;
        }

        const reading_history = this.getReadingHistory();

        if (reading_history === null) {
            return null;
        }

        const seen_cards = card_descriptors.filter(card => card.last_trial !== null);
        const now = new Date();
        const due_cards = seen_cards.filter(card => card.due_date < now);
        const maintenance_cards = seen_cards.filter(card => (
            (card.last_trial!.easiness >= 6) && (card.due_date > now)
        ));
        const continue_reading_document_histories = reading_history.document_histories.filter(d => (
            d.sentences_read < d.total_sentences
        )).slice(0, 3)
        const total_words_read = reading_history.words_read_by_day.reduce((n, d) => n + d.words, 0);
        const total_lemmas = reading_history.words_read_by_day.reduce((n, d) => n + d.new_lemmas, 0);

        const goal_cefr_level = CEFRLevels.find(l => l.lemmas > maintenance_cards.length) || CEFRLevels[CEFRLevels.length - 1];

        return (
            <div className="col-12 col-md-6 offset-md-3">
                <div className="row">
                    <div className="col-12">
                        <p>
                            Learning {seen_cards.length}/{card_descriptors.length} added words.
                            {' '}{due_cards.length} cards ready for review.
                        </p>
                        <p>
                            {maintenance_cards.length} cards in long-term memory (≥ 90 day review interval and not currently due).{' '}
                            This puts you at {Math.round(100*maintenance_cards.length/goal_cefr_level.lemmas)}% of
                            the way to {goal_cefr_level.name}!
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
                            Read {total_words_read} words so far, including {total_lemmas} distinct lemmas.
                        </p>
                    </div>
                    {continue_reading_document_histories.map(h => (
                        <div className="col-12" key={h.document.id}>
                            <Link to={`/document/${h.document.id}`}>
                                <div className="big button">
                                    Continue
                                    reading {h.document.title} ({Math.floor(100 * h.sentences_read / h.total_sentences)}%)
                                </div>
                            </Link>
                        </div>
                    ))}
                    <div className="col-6">
                        <Link to="/collections">
                            <div className="big button">
                                See collections
                            </div>
                        </Link>
                    </div>
                    <div className="col-6">
                        <div className="big button" onClick={() => this.setState({modal_type: "reading_history"})}>
                            See history
                        </div>
                    </div>
                    {this.metadataSections()}
                    {this.modal()}
                </div>
            </div>
        );
    }
}
