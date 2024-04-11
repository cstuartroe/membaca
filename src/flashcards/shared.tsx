import React from "react";
import {Link} from "react-router-dom";
import {Lemma} from "../models";

export function ProgressBar(props: {numerator: number, denominator: number}) {
    const {numerator, denominator} = props;

    return (
        <div className="col-12 cards-progress-bar">
            <div className="numbers">{numerator}/{denominator}</div>
            <div className="cards-progress" style={{width: `${Math.round(100 * numerator / denominator)}%`}}/>
        </div>
    );
}

export function SummarySlide(props: {trial_results: boolean[], isNew: boolean, lemmas: Lemma[], more: boolean}) {
    const {trial_results, isNew, lemmas, more} = props;

    const num_correct = trial_results.reduce((sum, correct, _) => sum + (correct ? 1 : 0), 0);

    return (
        <div className="col-12">
            <div className="sentence" style={{paddingTop: "5vh"}}>
                Great job! {num_correct}/{trial_results.length}{' '}
                ({Math.round(100 * num_correct / trial_results.length)}%){' '}
                correct.
            </div>
            <div className="sentence" style={{paddingTop: "5vh"}}>
                You {isNew ? "started" : "reviewed"} {lemmas.length} words:
            </div>
            {lemmas.map(lemma => (
                <div className="translation" key={lemma.id}>
                    <span style={{fontStyle: "italic"}}>{lemma.citation_form}</span>{' '}
                    "{lemma.translation}"
                </div>
            ))}
            {more && <a href={window.location.href}>
                <div className="big button">
                    Continue {isNew ? "learning" : "reviewing"}
                </div>
            </a>}
            <Link to="/dashboard">
                <div className="big button">
                    Back to dashboard
                </div>
            </Link>
        </div>
    );
}
