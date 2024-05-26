import React, { Component } from "react";
import {Language, Lemma, User} from "../models";
import {ProgressBar, SummarySlide} from "./shared";
import MultipleChoice from "./MultipleChoice";

type MetadataCardInfo = {
    lemma: Lemma,
    choices: string[],
    recommended_easiness: number,
}

type Props = {
    user: User,
    language: Language,
    new: boolean,
}

type State = {
    cards?: MetadataCardInfo[],
    more: boolean,
    index: number,
    still_showing_new: boolean,
    trial_results: boolean[],
}

export default class MetadataCards extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            more: true,
            index: 0,
            still_showing_new: props.new,
            trial_results: [],
        };
    }

    metadataField() {
        const params = new URLSearchParams(window.location.search);
        return params.get("metadata_field") as string;
    }

    componentDidMount() {
        const url = this.props.new ? "/api/metadata_cards/new" : "/api/metadata_cards/review";
        fetch(`${url}?language_id=${this.props.language.id}&metadata_field=${this.metadataField()}`)
            .then(res => res.json())
            .then(data => this.setState(data))
    }

    advance(correct: boolean, card: MetadataCardInfo) {
        const { cards, trial_results } = this.state;
        trial_results.push(correct);
        if (!correct) {
            cards!.push({
                ...card,
                recommended_easiness: 1,
            });
        }
        this.setState({
            index: this.state.index + 1,
            cards,
            trial_results,
        })
    }

    getLemmas() {
        const lemma_ids = new Set<number>();
        const lemmas: Lemma[] = [];
        this.state.cards!.forEach(card => {
            if (!lemma_ids.has(card.lemma.id)) {
                lemma_ids.add(card.lemma.id);
                lemmas.push(card.lemma);
            }
        })
        return lemmas;
    }

    showNewLemma() {
        const card = this.state.cards![this.state.index];

        return <>
            <div className="col-12">
                <div className="single-word">
                    {card.lemma.metadata[this.metadataField()]}
                    {' '}
                    {card.lemma.citation_form}
                </div>
            </div>
            <div className="col-12">
                <div className="translation">{card.lemma.translation}</div>
            </div>
            <div className="col-6 offset-3">
                <div
                    className="big button"
                    onClick={() => {
                        if (this.state.index === this.getLemmas().length - 1) {
                            this.setState({index: 0, still_showing_new: false});
                        } else {
                            this.setState({index: this.state.index + 1});
                        }
                    }}
                >
                    Next
                </div>
            </div>
        </>;
    }

    flashcard() {
        const card = this.state.cards![this.state.index];
        const metadata_field = this.metadataField();

        return (
            <MultipleChoice
                key={Math.random()}
                lemma={card.lemma}
                choices={card.choices}
                correct_answer={card.lemma.metadata[metadata_field]}
                submission_uri={"/api/metadata_trial"}
                extra_submission_params={{
                    metadata_field: metadata_field,
                }}
                recommended_easiness={card.recommended_easiness}
                mark_easiness={true}
                advance={correct => this.advance(correct, card)}
                question={_ => <>
                    <div className="col-12">
                        <div className="single-word">{card.lemma.citation_form}</div>
                    </div>
                    <div className="col-12">
                        <div className="translation">{card.lemma.translation}</div>
                    </div>
                </>}
                hide_answers={false}
            />
        );
    }

    mainContent() {
        if (this.state.still_showing_new) {
            return this.showNewLemma();
        }

        if (this.state.index === this.state.cards!.length) {
            return (
                <SummarySlide
                    trial_results={this.state.trial_results}
                    isNew={this.props.new}
                    lemmas={this.getLemmas()}
                    more={this.state.more}/>
            );
        }

        return this.flashcard();
    }

    progressBar() {
        const unique_lemmas = this.getLemmas().length;
        const numerator = this.state.index + ((this.props.new && !this.state.still_showing_new) ? unique_lemmas : 0);
        const denominator = this.state.cards!.length + (this.props.new ? unique_lemmas : 0);

        return <ProgressBar {...{numerator, denominator}}/>
    }

    render() {
        if (this.state.cards === undefined) {
            return null;
        }

        if (this.state.cards.length === 0) {
            return (
                <div className="col-12 col-md-8 offset-md-2 flashcard">
                    <div className="row">
                        <div className="col-12">
                            <div className="sentence">
                                {this.props.new && (
                                    "You don't have any new words to study. Try doing more word flashcards."
                                )}
                                {!this.props.new && (
                                    "You don't have any reviews right now. Try waiting a day or two, or check out " +
                                    "your review forecast on your dashboard."
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        return (
            <>
                {this.progressBar()}

                <div className="col-12 col-md-8 offset-md-2 flashcard">
                    <div className="row">
                        {this.mainContent()}
                    </div>
                </div>
            </>
        );
    }
}
