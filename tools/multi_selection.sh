#!/bin/bash

function print_menu() {
    local menu_items=($1)
    local current_selection="$2"
    local queued_selection=($3)
    local menu_size="${#menu_items[@]}"
    echo "${message}"
    for ((i = 0; i < "$menu_size"; ++i)); do
        if [ "${queued_selection[i]}" = "selected" ]; then
            if [ "$i" = "$current_selection" ]; then
                echo -e "\e[32m●  ${menu_items[i]}\e[m"
            else
                echo "●  ${menu_items[i]}"
            fi
        else
            if [ "$i" = "$current_selection" ]; then
                echo -e "\e[32m○  ${menu_items[i]}\e[m"
            else
                echo "   ${menu_items[i]}"
            fi
        fi
    done
}

function run_menu() {
    clear
    local menu_items=("$@")
    local current_selection=0
    local queued_selection=()
    local menu_size="${#menu_items[@]}"
    local menu_limit=$((menu_size - 1))

    for ((i = 0; i < "$menu_size"; ++i)); do
        queued_selection+=("nonselected")
    done

    print_menu "${menu_items[*]}" "$current_selection" "${queued_selection[*]}"
    while IFS= read -s -n 1 input; do
        case "$input" in
        $'\x1B') # ESC ASCII code (https://dirask.com/posts/ASCII-Table-pJ3Y0j)
            read -rsn1 -t 0.1 input
            if [ "$input" = "[" ]; then # occurs before arrow code
                read -rsn1 -t 0.1 input
                case "$input" in

                A) # Up Arrow
                    if [ "$current_selection" -ge 1 ]; then
                        current_selection=$((current_selection - 1))
                    fi
                    ;;
                B) # Down Arrow
                    if [ "$current_selection" -lt "$menu_limit" ]; then
                        current_selection=$((current_selection + 1))
                    fi
                    ;;
                esac
                clear
                print_menu "${menu_items[*]}" "$current_selection" "${queued_selection[*]}"
            fi
            read -rsn5 -t 0.1 # flushing stdin
            ;;
        $'\x20')
            if [ "${queued_selection[$current_selection]}" = "selected" ]; then
                queued_selection[$current_selection]="nonselected"
            else
                queued_selection[$current_selection]="selected"
            fi
            clear
            print_menu "${menu_items[*]}" "$current_selection" "${queued_selection[*]}"
            ;;
        "") # Enter key
            results=()
            for ((i = 0; i < "$menu_size"; ++i)); do
                if [ "${queued_selection[i]}" = "selected" ]; then
                    results+=("${menu_items[i]}")
                fi
            done
            echo "${results[*]}" >sel_res.txt
            return
            ;;
        esac
    done
}

declare -a menus=("$*")
run_menu ${menus[*]}
