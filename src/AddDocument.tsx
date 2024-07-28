import React, { Component, useState } from "react";
import {Navigate} from "react-router-dom";
import {safePost} from "./ajax_utils";
import {Collection, Language} from "./models";


type TextBoxProps = {
    text: string,
    offset: boolean,
    update: (s: string) => void,
    insert: () => void,
    drop: () => void,
}


function TextBox(props: TextBoxProps) {
    const { text, offset, update, insert, drop } = props;

    return <>
        <textarea
            style={{textAlign: "left", width: "100%"}}
            value={text}
            onChange={e => update(e.target.value)}/>
        <div className="button" onClick={() => {
            if (text === "") {
                drop()
            } else {
                insert()
            }
        }}>
            {text === "" ? "-" : "+"}
        </div>
    </>;
}


type SentencesOrTranslationRowsProps = {
    strings: string[] | undefined,
    update: (s: string[]) => void,
    insert: (i: number) => void,
    drop: (i: number) => void,
}


function SentencesOrTranslationRows(props: SentencesOrTranslationRowsProps) {
    const { strings, update, insert, drop } = props;

    if (strings === undefined) {
        const [content, setContent] = useState("");

        return <>
            <textarea
                style={{textAlign: "left", width: "100%"}}
                value={content}
                onChange={e => setContent(e.target.value)}/>
            <div className="button" onClick={() => update(breakIntoSentences(content))}>
                Break!
            </div>
        </>
    } else {
        return strings.map((text, i) => (
            <TextBox
                key={i}
                text={text}
                offset={false}
                update={s => {
                    const newStrings = strings;
                    newStrings[i] = s;
                    update(newStrings);
                }}
                insert={() => insert(i)}
                drop={() => drop(i)}/>
        ));
    }
}

type Props = {
    language: Language,
}

type State = {
    title: string,
    link: string,
    collections: Collection[],
    collection_id?: number,
    sentences?: string[],
    translations?: string[],
    documentId?: number,
}

const sentenceEnders = [".", "!", "?"];

function breakIntoSentences(s: string): string[] {
    const sentences = [];
    let currentSentenceStart = 0;
    let i = 0;
    while (i < s.length) {
        if (sentenceEnders.includes(s[i])) {
            i++;
            sentences.push(s.slice(currentSentenceStart, i));
            currentSentenceStart = i;
        } else {
            i++;
        }
    }
    if (currentSentenceStart < s.length) {
        sentences.slice(currentSentenceStart);
    }
    return sentences;
}

export default class AddDocument extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            title: "",
            link: "",
            collections: [],
        };
    }

    componentDidMount() {
        fetch(`/api/collections?language_id=${this.props.language.id}`)
            .then(res => res.json())
            .then(collections => this.setState({
                collections,
                collection_id: collections[0].id,
            }))
    }

    submit() {
        safePost(
            "/api/submit_document",
            {
                collection_id: this.state.collection_id,
                title: this.state.title,
                link: this.state.link,
                sentences: this.state.sentences,
                translations: this.state.translations,
            }
        ).then(res => res.json())
            .then(data => this.setState({documentId: data["document_id"]}))
    }

    setSentence(i: number, text: string) {
        const { sentences } = this.state;
        sentences![i] = text;
        this.setState({sentences});
    }

    setTranslation(i: number, text: string) {
        const { translations } = this.state;
        translations![i] = text;
        this.setState({translations});
    }

    insertSentence(i: number) {
        const { sentences } = this.state;
        sentences!.splice(i+1, 0, "");
        this.setState({sentences});
    }

    insertTranslation(i: number) {
        const { translations } = this.state;
        translations!.splice(i+1, 0, "");
        this.setState({translations});
    }

    dropSentence(i: number) {
        const { sentences } = this.state;
        sentences!.splice(i, 1);
        this.setState({sentences})
    }

    dropTranslation(i: number) {
        const { translations } = this.state;
        translations!.splice(i, 1);
        this.setState({translations});
    }

    sentenceBox(text: string, i: number) {
        return (
            <div className="col-6" key="sentence">
                <TextBox
                    text={text}
                    offset={false}
                    update={s => this.setSentence(i, s)}
                    insert={() => this.insertSentence(i)}
                    drop={() => this.dropSentence(i)}/>
            </div>
        );
    }

    translationBox(text: string, i: number, offset: boolean) {
        return (
            <div className={`col-6 ${offset ? "offset-6" : ""}`} key="translation">
                <TextBox
                    text={text}
                    offset={false}
                    update={s => this.setTranslation(i, s)}
                    insert={() => this.insertTranslation(i)}
                    drop={() => this.dropTranslation(i)}/>
            </div>
        )
    }

    sideBySideSentencesAndTranslations(sentences: string[], translations: string[]) {
        const rows: React.ReactNode[] = [];

        for (let i = 0; i < Math.max(sentences.length, translations.length); i++) {
            const boxes: React.ReactNode[] = [];
            if (sentences.length > i) {
                boxes.push(this.sentenceBox(sentences[i], i));
            }
            if (translations.length > i) {
                boxes.push(this.translationBox(translations[i], i, sentences.length <= i));
            }
            rows.push(
                <div className="col-12" key={i}>
                    <div className="row">
                        {boxes}
                    </div>
                </div>
            )
        }

        return rows;
    }

    rows() {
        const {sentences, translations } = this.state;

        if (sentences !== undefined && translations !== undefined) {
            return <>
                {this.sideBySideSentencesAndTranslations(sentences, translations)}

                <div className="col-4 offset-4 button" onClick={() => this.submit()}>
                    Submit!
                </div>
            </>;
        } else {
            return <>
                <div className="col-6">
                    <SentencesOrTranslationRows
                        strings={this.state.sentences}
                        update={sentences => this.setState({sentences})}
                        insert={i => this.insertSentence(i)}
                        drop={i => this.dropSentence(i)}/>
                </div>
                <div className="col-6">
                    <SentencesOrTranslationRows
                        strings={this.state.translations}
                            update={translations => this.setState({translations})}
                            insert={i => this.insertTranslation(i)}
                            drop={i => this.dropTranslation(i)}/>
                </div>
            </>;
        }
    }

    render() {
        if (this.state.documentId !== undefined) {
            return <Navigate to={`/document/${this.state.documentId}`}/>;
        }

        return (
            <>
                <div className="col-12">
                    <p style={{textAlign: "center"}}>Adding document for {this.props.language.name}</p>
                </div>
                <div className="col-12 col-md-8 offset-md-2">
                    <h2>Title</h2>
                    <input
                        type="text"
                        style={{textAlign: "center", width: "100%"}}
                        value={this.state.title}
                        onChange={e => this.setState({title: e.target.value})}/>
                    <h2>Collection</h2>
                    <select
                        value={this.state.collection_id}
                        onChange={e => this.setState({
                            collection_id: Number.parseInt(e.target.value),
                        })}
                    >
                        {this.state.collections.map(collection => (
                            <option value={collection.id} key={collection.id}>{collection.title}</option>
                        ))}
                    </select>
                    <h2>Link</h2>
                    <input
                        type="text"
                        style={{textAlign: "center", width: "100%"}}
                        value={this.state.link}
                        onChange={e => this.setState({link: e.target.value})}/>
                </div>
                <div className="col-6">
                    <h2>Sentences</h2>
                </div>
                <div className="col-6">
                    <h2>Translations</h2>
                </div>
                {this.rows()}
            </>
        );
    }
}
