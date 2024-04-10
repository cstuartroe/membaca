import {EASINESS_DAYS, Lemma} from "../models";
import React, {Component} from "react";
import {safePost} from "../ajax_utils";
import classNames from "classnames";

function ChooseEasiness(props: {lemma: Lemma, recommended_easiness: number, setEasiness: (n: number) => void}) {
    const {lemma, recommended_easiness, setEasiness} = props;

    return (
        <div className="col-12">
            <div className="translation">
                When would you like to see this word{' '}
                <span style={{fontStyle: "italic"}}>{lemma.citation_form}</span>{' '}
                "{lemma.translation}"
                {' '}next?
            </div>
            <div className="row">
                {EASINESS_DAYS.map((days, easiness) => (
                    <div className="col-3" key={easiness}>
                        <div
                            className={classNames("big", "button", {correct: recommended_easiness === easiness})}
                            onClick={() => setEasiness(easiness)}
                        >
                            {(easiness === 0) ? "Later today" : `${days} days`}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

type MultipleChoiceProps = {
    question: (reveal_answer: boolean) => React.ReactNode,
    lemma: Lemma,
    choices: string[],
    correct_answer: string,
    submission_uri: string,
    extra_submission_params: Object,
    recommended_easiness: number,
    mark_easiness: boolean,
    advance: (correct: boolean) => void,
}

type MultipleChoiceState = {
    choice?: string,
    easiness?: number,
}

export default class MultipleChoice extends Component<MultipleChoiceProps, MultipleChoiceState> {
    constructor(props: MultipleChoiceProps) {
        super(props);
        this.state = {
        }
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
        safePost(
            this.props.submission_uri,
            {
                lemma_id: this.props.lemma.id,
                choices: this.props.choices,
                choice: this.state.choice,
                correct: this.correct(),
                easiness: this.correct() ? this.state.easiness : 0,
                ...this.props.extra_submission_params,
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
            {this.props.choices.map(choice => {
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
        return (
            <ChooseEasiness
                lemma={this.props.lemma}
                recommended_easiness={this.props.recommended_easiness}
                setEasiness={easiness => this.setState({easiness})}/>
        );
    }

    mainContent() {
        if (this.state.choice === undefined || (!this.correct() && this.state.easiness === undefined)) {
            return this.answerChoiceButtons();
        } else if (this.state.easiness === undefined) {
            return this.easinessButtons();
        } else {
            return null;
        }
    }

    render() {
        const reveal_answer = this.state.choice !== undefined;

        return (
            <>
                {this.props.question(reveal_answer)}
                {this.mainContent()}
            </>
        );
    }
}