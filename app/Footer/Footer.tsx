"use client";

import Link from "next/link";
import Image from "next/image";

import { FaGithub } from "react-icons/fa";
import { MdArrowOutward } from "react-icons/md";
import { FaXTwitter } from "react-icons/fa6";
import { FaProductHunt } from "react-icons/fa";

import Logo from "@/app/assets/Devmatchups.svg";
import SwocLogo from "@/app/assets/SWOC.png";
import HacktoberfestLogo from "@/app/assets/Hacktoberfest.png";

export default function Footer() {
  return (
    <footer className="w-full bg-gradient-to-br from-[#f0f4ff] via-[#e8edf8] to-[#d9e2f1] dark:from-[#1c1c1e] dark:via-[#2b2b2d] dark:to-[#1e1e1f] text-gray-900 dark:text-gray-200 border-t border-gray-300 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
        {/* Brand Info */}
        <div className="space-y-4">
          <Link href="/" className="flex items-center gap-3">
            <Image
              src={Logo}
              alt="Synapse Logo"
              className="w-10 h-10 object-cover"
            />
            <span className="text-2xl font-bold">Synapse</span>
          </Link>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Team up for success in every hackathon. <br />
            Build your dream hackathon team with DevMatchups!
          </p>
        </div>

       {/* Supported & Contribute
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-lg mb-2">Supported by</h3>
            <div className="flex gap-4 items-center">
              <Image src={SwocLogo} alt="SWOC" width={40} height={40} />
              <Image
                src={HacktoberfestLogo}
                alt="Hacktoberfest"
                width={40}
                height={40}
              />
            </div>
          </div>
          <div>
            <h3 className="font-semibold text-lg mb-2">Contribute</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="https://github.com/harsh3dev/DevMatchups"
                  target="_blank"
                  className="group flex items-center gap-1 hover:text-blue-600"
                >
                  Star on GitHub
                  <MdArrowOutward className="transition-opacity opacity-0 group-hover:opacity-100" />
                </Link>
              </li>
              <li>
                <Link
                  href="https://github.com/sponsors/harsh3dev"
                  target="_blank"
                  className="group flex items-center gap-1 hover:text-blue-600"
                >
                  Sponsor on GitHub
                  <MdArrowOutward className="transition-opacity opacity-0 group-hover:opacity-100" />
                </Link>
              </li>
            </ul>
          </div>
        </div> */}

        {/* Contact */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Contact</h3>
          <ul className="space-y-2 text-sm">
            <li>
              <Link
                href="mailto:raghul.m.2024.cse@rajalakshmi.edu.in"
                target="_blank"
                className="group flex items-center gap-1 hover:underline"
              >
                raghul.m.2024.cse@rajalakshmi.edu.in
                <MdArrowOutward className="transition-opacity opacity-0 group-hover:opacity-100" />
              </Link>
            </li>
            <li>
              <Link
                href="ritheshmadhav.s.2024.cse@rajalakshmi.edu.in"
                target="_blank"
                className="group flex items-center gap-1 hover:underline"
              >
                ritheshmadhav.s.2024.cse@rajalakshmi.edu.in
                <MdArrowOutward className="transition-opacity opacity-0 group-hover:opacity-100" />
              </Link>
            </li>
            <li>
              <Link
                href="https://forms.gle/BsppX1H3HGbA6ioaA"
                target="_blank"
                className="group flex items-center gap-1 hover:underline"
              >
                Report a bug!
                <MdArrowOutward className="transition-opacity opacity-0 group-hover:opacity-100" />
              </Link>
            </li>
          </ul>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-300 dark:border-gray-700 mt-4 py-6 text-center text-sm text-gray-600 dark:text-gray-400">
        <p className="mb-3">
          Created by{" "}
          <Link
            href="https://www.linkedin.com/in/Raghul M/"
            target="_blank"
            className="text-blue-600 hover:underline"
          >
            Raghul M
          </Link>{" "}
          &{" "}
          <Link
            href="https://www.linkedin.com/in/Rithesh Madhav.S/"
            target="_blank"
            className="text-blue-600 hover:underline"
          >
            Rithesh Madhav.S
          </Link>
        </p>
        <div className="flex justify-center items-center gap-4 text-xl">

          <Link
            href="https://github.com/Raghul2808/Synapse"
            target="_blank"
            className="hover:text-black dark:hover:text-white"
          >
            <FaGithub />
          </Link>
        </div>
      </div>
    </footer>
  );
}
