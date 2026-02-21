import React from "react";

const technicalContributors = [
  {
    name: "Shivam Verma",
    image: "Contributors/IMG-20260124-WA0066-cpy.jpg",
    linkedin: "https://www.linkedin.com/in/shivam-verma-332710237/",
  },
  {
    name: "Nikhil Kumar",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/tech2",
  },
  {
    name: "Suhani Nagpal",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/tech3",
  },
  {
    name: "Harshita Gupta",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/tech4",
  },
  {
    name: "Nishtha Dhawan",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/tech5",
  },
];

const nonTechnicalContributors = [
  {
    name: "Vishesh Gupta",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/nontech1",
  },
  {
    name: "Bhavya Sabharwal",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/nontech2",
  },
  {
    name: "Deeksha Gupta",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/nontech3",
  },
  {
    name: "Kshtiz Aggarwal",
    image: "https://via.placeholder.com/200",
    linkedin: "https://linkedin.com/in/nontech4",
  },
];

const ContributorCard = ({ person }) => {
  return (
    <div
      onClick={() => window.open(person.linkedin, "_blank")}
      className="flex flex-col items-center cursor-pointer group transition transform hover:scale-105"
    >
      <img
        src={person.image}
        alt={person.name}
        className="w-32 h-32 md:w-40 md:h-40 rounded-full object-cover border-4 border-gray-200 group-hover:border-blue-500 transition"
      />
      <p className="mt-4 text-lg font-medium text-gray-800 group-hover:text-blue-600">
        {person.name}
      </p>
    </div>
  );
};

function About() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-semibold text-center mb-6">About <span className="font-bold text-5xl">AERISK</span></h1>
      <p className="text-lg text-gray-600 text-center mb-12">
        Meet the team behind our Risk Analysis and Fault Prediction System.
      </p>

      {/* Technical Contributors */}
      <div className="mb-16">
        <h2 className="text-2xl font-semibold text-center mb-8">
          Technical Contributors
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-8 justify-items-center">
          {technicalContributors.map((person, index) => (
            <ContributorCard key={index} person={person} />
          ))}
        </div>
      </div>

      {/* Non-Technical Contributors */}
      <div>
        <h2 className="text-2xl font-semibold text-center mb-8">
          Non-Technical Contributors
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-8 justify-items-center">
          {nonTechnicalContributors.map((person, index) => (
            <ContributorCard key={index} person={person} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default About;