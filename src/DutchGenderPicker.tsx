import React, { Component } from "react";
import {Lemma} from "./models";
import {safePost} from "./ajax_utils";
import classNames from "classnames";

type SingleWordPickerProps = {
    lemma: Lemma,
}

type SingleWordPickerState = {
    picked_gender?: string,
}

class SingleWordPicker extends Component<SingleWordPickerProps, SingleWordPickerState> {
    constructor(props: SingleWordPickerProps) {
        super(props);
        this.state = {
        }
    }

    saveGender(gender: string) {
        safePost(
            "/api/lemma",
            {
                id: this.props.lemma.id,
                "metadata:gender": gender,
            }
        ).then(res => {
            if (res.ok) {
                this.setState({picked_gender: gender})
            }
        })
    }

    genderButton(gender: string) {
        return (
            <div className="col-3">
                <div
                    className={classNames("button", "noto", {correct: this.state.picked_gender === gender})}
                    onClick={() => this.saveGender(gender)}
                >
                    {gender}
                </div>
            </div>
        );
    }

    render() {
        const {lemma} = this.props;

        return <div className="row">
            <div className="col-12 dutch-gender-picker">
                <span style={{fontStyle: "italic"}}>{lemma.citation_form}</span>{' '}
                "{lemma.translation}"
            </div>
            <div className="col-12 col-md-6 offset-md-3">
            <div className="row">
                    {this.genderButton("de")}
                    {this.genderButton("het")}
                    {this.genderButton("de/het")}
                    {this.genderButton("-")}
                </div>
            </div>
            {!this.state.picked_gender && (
                <>
                    <div className="col-6" style={{paddingBottom: "20px"}}>
                        <iframe
                            src={`https://nl.wiktionary.org/wiki/${lemma.citation_form}`}
                            width="100%"
                            height="800px"
                        />
                    </div>
                    <div className="col-6" style={{paddingBottom: "20px"}}>
                        <iframe
                            src={`https://www.woorden.org/woord/${lemma.citation_form}`}
                            width="100%"
                            height="800px"
                        />
                    </div>
                </>
            )}
        </div>;
    }
}

type Props = {}

type State = {
    lemmas?: Lemma[],
}

export default class DutchGenderPicker extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {};
    }


    componentDidMount() {
        fetch("/api/dutch_genderless_words")
            .then(res => res.json())
            .then(lemmas => this.setState({lemmas}))
    }


    render() {
        const {lemmas} = this.state;

        if (lemmas === undefined) {
            return null;
        }

        return (
            <div className="col-12 col-md-8 offset-md-2">
                {lemmas.map(lemma => <SingleWordPicker lemma={lemma} key={lemma.id}/>)}
            </div>
        );
    }
}
