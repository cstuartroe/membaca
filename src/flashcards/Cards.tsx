import React, { Component } from "react";
import {Language, Lemma, Sentence, Substring, User} from "../models";
import {ProgressBar, SummarySlide} from "./shared";
import MultipleChoice from "./MultipleChoice";

function shuffle<T>(array: T[]) {
    let currentIndex = array.length;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

        // Pick a remaining element...
        let randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
            array[randomIndex], array[currentIndex]];
    }
}

type ClozeInfo = {
    sentence: Sentence,
    slash_separated_word: string,
    substrings: Substring[],
}

type StandardCardInfo = {
    lemma_id: number,
    trial_type: "cc" | "ct",
    answer: null,
    other_choices: string[],
    recommended_easiness: number,
}

type ClozeCardInfo = {
    lemma_id: number,
    trial_type: "cz",
    answer: ClozeInfo,
    other_choices: string[],
    recommended_easiness: number,
};

type CardInfo = StandardCardInfo | ClozeCardInfo;

type LemmaDict = {[key: number]: Lemma};

type Props = {
    user: User,
    language: Language,
    new: boolean,
}

type State = {
    lemmas_by_id?: LemmaDict,
    cards: CardInfo[],
    more: boolean,
    index: number,
    still_showing_new_lemmas: boolean,
    trial_results: boolean[],
}

export default class Cards extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            cards: [],
            more: true,
            index: 0,
            still_showing_new_lemmas: props.new,
            trial_results: [],
        };
    }

    componentDidMount() {
        const url = this.props.new ? "/api/cards/new" : "/api/cards/review";
        fetch(`${url}?language_id=${this.props.language.id}`)
            .then(res => res.json())
            .then(data => this.setState({...data}))
    }

    advance(correct: boolean, card: CardInfo) {
        const { cards, trial_results } = this.state;
        trial_results.push(correct);
        if (!correct) {
            cards.push({
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

    shouldMarkEasiness() {
        const lemma_id = this.state.cards[this.state.index].lemma_id;
        let lastCardWithLemma = -1;
        this.state.cards.forEach((card, i) => {
            if (card.lemma_id === lemma_id) {
                lastCardWithLemma = i;
            }
        });
        return this.state.index === lastCardWithLemma;
    }

    showNewLemma() {
        const lemmas_by_id: LemmaDict = this.state.lemmas_by_id as LemmaDict;

        const lemma_ids = [...Object.keys(lemmas_by_id)]
        lemma_ids.sort()
        const lemma = lemmas_by_id[Number.parseInt(lemma_ids[this.state.index])]

        return <>
            <div className="col-12">
                <div className="single-word">{lemma.citation_form}</div>
            </div>
            <div className="col-12">
                <div className="translation">{lemma.translation}</div>
            </div>
            <div className="col-6 offset-3">
                <div
                    className="big button"
                    onClick={() => {
                        if (this.state.index === lemma_ids.length - 1) {
                            this.setState({index: 0, still_showing_new_lemmas: false});
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
        const currentCard = this.state.cards[this.state.index];
        switch (currentCard.trial_type) {
            case "cz": return this.clozeCard(currentCard);
            default: return this.standardCard(currentCard);
        }
    }

    multipleChoice(card: CardInfo, lemma: Lemma, correct_answer: string, question: (reveal_answer: boolean) => React.ReactNode) {
        const choices: string[] = [
            correct_answer,
            ...card.other_choices,
        ];

        shuffle(choices);

        return (
            <MultipleChoice
                key={Math.random()}
                question={question}
                lemma={lemma}
                choices={choices}
                correct_answer={correct_answer}
                submission_uri={"/api/trial"}
                extra_submission_params={{
                    trial_type: card.trial_type,
                    sentence_id: (card.trial_type == "cz") ? card.answer.sentence.id : null,
                }}
                recommended_easiness={card.recommended_easiness}
                mark_easiness={this.shouldMarkEasiness()}
                advance={correct => this.advance(correct, card)}
            />
        );
    }

    standardCard(card: StandardCardInfo) {
        const choosingTranslation = card.trial_type === "ct";
        const lemma = this.state.lemmas_by_id![card.lemma_id];
        const question = choosingTranslation ? lemma.citation_form : lemma.translation;
        const correct_answer = choosingTranslation ? lemma.translation : lemma.citation_form;

        return this.multipleChoice(card, lemma, correct_answer, _ => (
            <div className="col-12">
                <div className={choosingTranslation ? "single-word" : "sentence"}>{question}</div>
            </div>
        ))
    }

    clozeCard(card: ClozeCardInfo) {
        const lemma = this.state.lemmas_by_id![card.lemma_id];

        return this.multipleChoice(card, lemma, card.answer.slash_separated_word, reveal_answer => {
            let sentenceWithUnderscores: React.ReactNode[] = [];
            let prevEnd = 0;

            card.answer.substrings.forEach(substring => {
                sentenceWithUnderscores.push(card.answer.sentence.text.substring(prevEnd, substring.start));
                if (reveal_answer) {
                    sentenceWithUnderscores.push(
                        <span style={{textDecoration: "underline"}}>
                            {card.answer.sentence.text.substring(substring.start, substring.end)}
                        </span>
                    );
                } else {
                    sentenceWithUnderscores.push("\uff3f\uff3f")
                }
                prevEnd = substring.end;
            });
            sentenceWithUnderscores.push(card.answer.sentence.text.substring(prevEnd));

            return <>
                <div className="col-12">
                    <div className="sentence">{sentenceWithUnderscores}</div>
                </div>
                <div className="col-12">
                    <div className="translation">{card.answer.sentence.translation}</div>
                </div>
            </>;
        })
    }

    mainContent() {
        if (this.state.still_showing_new_lemmas) {
            return this.showNewLemma();
        }

        if (this.state.index === this.state.cards.length) {
            return (
                <SummarySlide
                    trial_results={this.state.trial_results}
                    isNew={this.props.new}
                    lemmas={[...Object.values(this.state.lemmas_by_id!)].sort((a, b) => a.id - b.id)}
                    more={this.state.more}/>
            );
        }

        return this.flashcard();
    }

    progressBar() {
        const num_lemmas = [...Object.keys(this.state.lemmas_by_id!)].length;
        const numerator = this.state.index + ((this.props.new && !this.state.still_showing_new_lemmas) ? num_lemmas : 0);
        const denominator = this.state.cards.length + (this.props.new ? num_lemmas : 0);

        return <ProgressBar {...{numerator, denominator}}/>
    }


    render() {
        if (this.state.lemmas_by_id === undefined) {
            return null;
        }

        if (this.state.cards.length === 0) {
            return (
                <div className="col-12 col-md-8 offset-md-2 flashcard">
                    <div className="row">
                        <div className="col-12">
                            <div className="sentence">
                                {this.props.new && (
                                    "You don't have any new words to learn. Try adding more sentences from a document."
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
