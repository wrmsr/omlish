(ns reader-demo.core
  (:require [clojure.set :as set]))

;; Metadata, quoting, and var quote
(def ^:private ^String ^{:doc "A demo constant"} demo-const "Hello, world!")

(defn greet [] (println demo-const))

;; Symbols, keywords, and namespaced keywords
(def sym 'foo)
(def kw :some/keyword)
(def kw-auto ::local)

;; Lists, vectors, maps, and sets
(def some-data
  {:list '(1 2 3)
   :vector [4 5 6]
   :map {:a 1 :b 2}
   :set #{1 2 3}})

;; Syntax quoting and unquoting
(defmacro make-vec [x]
  `(vector ~x ~@x))

(def example-vec (make-vec [1 2 3]))

;; Anonymous function and reader macro
(def doubled (map #(* 2 %) [1 2 3]))

;; Deref and var quote
(def my-atom (atom 42))
(def current-value @my-atom)
(def var-ref #'demo-const)

;; Reader tagged literals
(def some-time #inst "2025-05-06T12:34:56.789Z")
(def some-uuid #uuid "123e4567-e89b-12d3-a456-426614174000")

;; Namespaced map
(def user {:user/id 1 :user/name "Alice"})

(defn show-ns-map []
  (let [m #:db{:id 42 :name "foo"}]
    (println m)))

;; Ignoring forms with #_
#_(def should-be-ignored (println "This won't be evaluated"))

;; Macro system and gensym
(defmacro once-only [expr]
  `(let [val# ~expr]
     (println "Once-only val:" val#)
     val#))

;; Using the macro
(def result (once-only (+ 1 2)))

;; Set operations and function definitions
(defn show-set-diff []
  (println (set/difference #{1 2 3} #{2})))

;; Run the demo
(defn -main []
  (greet)
  (println "Some data:" some-data)
  (println "Example vec from macro:" example-vec)
  (println "Doubled:" doubled)
  (println "Current atom value:" current-value)
  (println "Demo const via var:" @var-ref)
  (println "Time:" some-time)
  (println "UUID:" some-uuid)
  (show-ns-map)
  (show-set-diff))

(comment
  ;; Top-level comment form, won't be compiled
  (-main))
