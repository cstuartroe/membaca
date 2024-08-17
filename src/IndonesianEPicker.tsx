import React, { Component } from "react";
import {Lemma} from "./models";
import {safePost} from "./ajax_utils";

type SingleWordPickerProps = {
    lemma: Lemma,
}

type SingleWordPickerState = {
    current_word: string,
}

class SingleWordPicker extends Component<SingleWordPickerProps, SingleWordPickerState> {
    constructor(props: SingleWordPickerProps) {
        super(props);
        this.state = {
            current_word: props.lemma.citation_form,
        }
    }

    componentDidUpdate(prevProps: Readonly<SingleWordPickerProps>, prevState: Readonly<SingleWordPickerState>, snapshot?: any) {
        const {current_word} = this.state;

        if (!current_word.includes("e")) {
            safePost(
                "/api/lemma",
                {
                    id: this.props.lemma.id,
                    citation_form: current_word,
                }
            )
        }
    }

    eButton(i: number, e_variant: string, top: string) {
        const {current_word} = this.state;

        return (
            <div
                className="button unicode e-option"
                style={{top}}
                onClick={() => this.setState({
                    current_word: current_word.slice(0, i) + e_variant + current_word.slice(i + 1),
                })}
            >
                {e_variant}
            </div>
        );
    }

    ePicker(i: number) {
        const {current_word} = this.state;

        return (
            <span style={{position: "relative"}}>
                e
                {this.eButton(i, "é", "-3vh")}
                {this.eButton(i, "ê", " 3vh")}
            </span>
        );
    }

    render() {
        const {current_word} = this.state;

        const children: React.ReactNode[] = [];

        for (let i = 0; i < current_word.length; i++) {
            const letter = current_word.charAt(i);
            if (letter === "e") {
                children.push(this.ePicker(i));
            } else {
                children.push(letter);
            }
        }

        return <div className="row">
            <div className="col-12 indonesian-e-picker">
                <a
                    href={`https://en.wiktionary.org/wiki/${current_word}#Indonesian`}
                    target="_blank"
                >
                    {children}
                </a>
            </div>
        </div>;
    }
}

type Props = {
}

type State = {
    lemmas?: Lemma[],
}

export default class IndonesianEPicker extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        fetch("/api/indonesian_e")
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
