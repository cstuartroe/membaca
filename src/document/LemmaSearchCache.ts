import {Lemma} from "../models";

export type SearchResult = {
    lemma: Lemma,
    exact_match: boolean,
}

type SearchResults = {
    results: SearchResult[],
    no_lemma_matched: boolean,
}

export default class LemmaSearchCache {
    language_id: number
    cachedSearches: {[query: string]: Promise<SearchResults>}

    constructor(language_id: number) {
        this.language_id = language_id;
        this.cachedSearches = {};
    }

    search(query: string): Promise<SearchResults> {
        if (this.cachedSearches[query] !== undefined) {
            return this.cachedSearches[query];
        }

        const promise: Promise<SearchResults> = fetch(`/api/search_lemmas?language_id=${this.language_id}&q=${query}&num_results=5`)
            .then(res => res.json());

        this.cachedSearches[query] = promise;
        return promise;
    }

    clear(query: string) {
        delete this.cachedSearches[query];
    }
}