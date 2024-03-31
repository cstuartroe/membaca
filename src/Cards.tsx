import React, { Component } from "react";
import {Language, Lemma, Sentence, Substring, TrialType, User} from "./models";
import {safePost} from "./ajax_utils";
import classNames from "classnames";

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

const EASINESS_DAYS = [
    0,
    1,
    2,
    4,
    10,
    30,
    90,
    365,
]

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

type MultipleChoiceProps = {
    correct_answer: string,
    card: CardInfo,
    advance: (correct: boolean) => void,
    mark_easiness: boolean,
}

type MultipleChoiceState = {
    choices: string[],
    choice?: string,
    easiness?: number,
}

class MultipleChoice extends Component<MultipleChoiceProps, MultipleChoiceState> {
    constructor(props: MultipleChoiceProps) {
        super(props);
        this.state = {
            choices: this.randomAnswers(),
        }
    }

    randomAnswers() {
        const { correct_answer, card } = this.props;

        const choices: string[] = [
            correct_answer,
            ...card.other_choices,
        ];

        shuffle(choices);

        return choices;
    }

    correct() {
        return this.state.choice === this.props.correct_answer;
    }

    componentDidUpdate(prevProps: Readonly<MultipleChoiceProps>, prevState: Readonly<MultipleChoiceState>, snapshot?: any) {
        if (this.state.easiness !== undefined) {
            this.submitTrial();
        }
    }

    submitTrial() {
        const {card} = this.props;

        safePost(
            "/api/trial",
            {
                lemma_id: card.lemma_id,
                trial_type: card.trial_type,
                sentence_id: (card.trial_type == "cz") ? card.answer.sentence.id : null,
                choices: this.state.choices,
                choice: this.state.choice,
                easiness: this.correct() ? this.state.easiness : 0,
                correct: this.correct(),
            }
        )
            .then(res => {
                if (res.ok) {
                    this.props.advance(this.correct());
                }
            })
    }

    answerChoiceButtons() {
        return <>
            {this.state.choices.map(choice => {
                const correct = choice === this.props.correct_answer;
                const showColor = this.state.choice !== undefined;
                return (
                    <div className="col-6" key={choice}>
                        <div
                            className={classNames("big", "button", "unicode", {
                                correct: showColor && correct,
                                incorrect: showColor && !correct,
                            })}
                            onClick={() => {
                                if (!showColor) {
                                    const easiness = (correct && !this.props.mark_easiness) ? 0 : undefined;
                                    this.setState({
                                        choice,
                                        easiness,
                                    })
                                } else {
                                    if (this.correct()) {
                                        throw "Unexpected logical turn";
                                    }
                                    if (correct) {
                                        this.setState({easiness: 0})
                                    }
                                }
                            }}>
                            {choice}
                        </div>
                    </div>
                );
            })}
        </>
    }

    easinessButtons() {
        return <div className="col-12">
            <div className="translation">When would you like to see this word next?</div>
            <div className="row">
                {EASINESS_DAYS.map((days, easiness) => (
                    <div className="col-3" key={easiness}>
                        <div
                            className={classNames("big", "button", {correct: this.props.card.recommended_easiness === easiness})}
                            onClick={() => this.setState({easiness})}
                        >
                            {(easiness === 0) ? "Later today" : `${days} days`}
                        </div>
                    </div>
                ))}
            </div>
        </div>;
    }

    render() {
        if (this.state.choice === undefined || (!this.correct() && this.state.easiness === undefined)) {
            return this.answerChoiceButtons();
        } else if (this.state.easiness === undefined) {
            return this.easinessButtons();
        } else {
            return null;
        }
    }
}

type Props = {
    user: User,
    language: Language,
    new: boolean,
}

type State = {
    lemmas_by_id?: LemmaDict,
    cards: CardInfo[],
    index: number,
    still_showing_new_lemmas: boolean,
}

export default class Cards extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            cards: [],
            index: 0,
            still_showing_new_lemmas: props.new,
        };
    }

    componentDidMount() {
        const url = this.props.new ? "/api/cards/new" : "/api/cards/review";
        fetch(url)
            .then(res => res.json())
            .then(data => this.setState({
                lemmas_by_id: data.lemmas_by_id,
                cards: data.cards,
            }))
    }

    advance(correct: boolean, card: CardInfo) {
        const cards = this.state.cards;
        if (!correct) {
            cards.push(card);
        }
        this.setState({
            index: this.state.index + 1,
            cards,
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

        return (
            <div className="col-12 col-md-8 offset-md-2 flashcard">
                <div className="row">
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
                </div>
            </div>
        );
    }

    flashcard() {
        const currentCard = this.state.cards[this.state.index];
        switch (currentCard.trial_type) {
            case "cz": return this.clozeCard(currentCard);
            default: return this.standardCard(currentCard);
        }
    }

    standardCard(card: StandardCardInfo) {
        const choosingTranslation = card.trial_type === "ct";
        const lemma = this.state.lemmas_by_id![card.lemma_id];
        const question = choosingTranslation ? lemma.citation_form : lemma.translation;
        const correct_answer = choosingTranslation ? lemma.translation : lemma.citation_form;

        return (
            <div className="col-12 col-md-8 offset-md-2 flashcard">
                <div className="row">
                    <div className="col-12">
                        <div className={choosingTranslation ? "single-word" : "sentence"}>{question}</div>
                    </div>
                    <MultipleChoice
                        key={Math.random()}
                        card={card}
                        correct_answer={correct_answer}
                        advance={correct => this.advance(correct, card)}
                        mark_easiness={this.shouldMarkEasiness()}
                    />
                </div>
            </div>
        );
    }

    clozeCard(card: ClozeCardInfo) {
        let sentenceWithUnderscores = "";
        let prevEnd = 0;

        card.answer.substrings.forEach(substring => {
            sentenceWithUnderscores += card.answer.sentence.text.substring(prevEnd, substring.start);
            sentenceWithUnderscores += "\uff3f";
            prevEnd = substring.end;
        });
        sentenceWithUnderscores += card.answer.sentence.text.substring(prevEnd);

        return (
            <div className="col-12 col-md-8 offset-md-2 flashcard">
                <div className="row">
                    <div className="col-12">
                        <div className="sentence">{sentenceWithUnderscores}</div>
                    </div>
                    <div className="col-12">
                        <div className="translation">{card.answer.sentence.translation}</div>
                    </div>
                    <MultipleChoice
                        key={Math.random()}
                        card={card}
                        correct_answer={card.answer.slash_separated_word}
                        advance={correct => this.advance(correct, card)}
                        mark_easiness={this.shouldMarkEasiness()}
                    />
                </div>
            </div>
        );
    }

    summarySlide() {
        return null;
    }


    render() {
        if (this.state.lemmas_by_id === undefined) {
            return null;
        }

        if (this.state.still_showing_new_lemmas) {
            return this.showNewLemma();
        }

        if (this.state.index === this.state.cards.length) {
            return this.summarySlide();
        }

        return this.flashcard();
    }
}
